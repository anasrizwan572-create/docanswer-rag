from abc import ABC, abstractmethod
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import chromadb
from rank_bm25 import BM25Okapi

from api.config import settings
from api.embeddings import get_embedding_function
from api.models import RetrievedChunk
from api.utils import ensure_index_ready

STOP_WORDS = {
    "what", "when", "where", "which", "who", "whom", "whose", "why", "how",
    "many", "much", "does", "have", "been", "were", "this", "that", "these",
    "those", "from", "with", "about", "into", "through", "during", "before",
    "after", "above", "below", "between", "under", "again", "further", "then",
    "once", "here", "there", "both", "each", "few", "more", "most", "other",
    "some", "such", "only", "own", "same", "than", "too", "very", "can",
    "will", "just", "should", "now"
}


class Retriever(ABC):
    """
    Abstract Retriever Interface.
    Enables swapping ChromaDB for Chroma Cloud or pgvector seamlessly in future versions.
    """
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 4) -> List[RetrievedChunk]:
        """
        Retrieve the most relevant passages for a query with citation metadata and scores.
        """
        pass


class HybridRetriever(Retriever):
    """
    Hybrid retriever combining dense vector similarity with BM25 lexical search.
    Merges candidates using Reciprocal Rank Fusion (RRF) and performs cross-feature reranking.
    """
    def __init__(self, index_dir: Path = None):
        if index_dir is None:
            index_dir = ensure_index_ready()
        self.index_dir = index_dir

        # 1. Load Chroma Vector Store
        chroma_dir = self.index_dir / "chroma_db"
        if not chroma_dir.exists():
            raise FileNotFoundError(f"Chroma index not found at {chroma_dir}. Run scripts/ingest.py first.")

        self.chroma_client = chromadb.PersistentClient(path=str(chroma_dir))
        self.embedding_fn = get_embedding_function()
        self.collection = self.chroma_client.get_collection(
            name="hr_policy",
            embedding_function=self.embedding_fn
        )

        # 2. Load BM25 Lexical Index
        bm25_file = self.index_dir / "bm25_index.json"
        if not bm25_file.exists():
            raise FileNotFoundError(f"BM25 index not found at {bm25_file}. Run scripts/ingest.py first.")

        with open(bm25_file, "r", encoding="utf-8") as f:
            bm25_data = json.load(f)

        self.chunks_data = bm25_data["chunks"]
        self.chunk_map = {c["chunk_id"]: c for c in self.chunks_data}
        self.tokenized_corpus = bm25_data["tokenized_corpus"]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def _dense_search(self, query: str, n_results: int = 8) -> List[Tuple[str, float]]:
        """
        Executes dense vector similarity search in Chroma.
        Returns list of (chunk_id, similarity_score).
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        dense_ranked = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            distances = results["distances"][0] if results["distances"] else [0.0] * len(ids)
            for cid, dist in zip(ids, distances):
                # Cosine distance bounded to [0.0, 1.0] similarity
                sim = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                dense_ranked.append((cid, sim))
        return dense_ranked

    def _sparse_search(self, query: str, n_results: int = 8) -> List[Tuple[str, float]]:
        """
        Executes BM25 keyword search.
        Returns list of (chunk_id, normalized_bm25_score).
        """
        raw_tokens = re.findall(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*", query.lower())
        tokens = [w for w in raw_tokens if w not in STOP_WORDS]
        if not tokens:
            tokens = raw_tokens
        if not tokens:
            return []

        doc_scores = self.bm25.get_scores(tokens)
        max_score = max(doc_scores) if len(doc_scores) > 0 and max(doc_scores) > 0 else 1.0

        scored_pairs = []
        for idx, score in enumerate(doc_scores):
            if score > 0:
                cid = self.chunks_data[idx]["chunk_id"]
                norm_score = min(1.0, score / max_score)
                scored_pairs.append((cid, norm_score))

        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:n_results]

    def _rerank(self, candidates: List[Dict[str, Any]], query: str, top_k: int = 4) -> List[RetrievedChunk]:
        """
        Reranks top candidates down to top_k.
        Uses composite scoring: dense similarity, BM25 keyword alignment, and exact phrase boost.
        Sorts on unclipped score to preserve rank separation.
        """
        query_lower = query.lower()
        query_tokens = [w for w in re.findall(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*", query_lower) if w not in STOP_WORDS]

        scored_candidates = []
        for cand in candidates:
            chunk = cand["chunk"]
            text_lower = chunk["text"].lower()
            section_lower = chunk["section"].lower()

            dense_score = cand.get("dense_score", 0.0)
            bm25_score = cand.get("bm25_score", 0.0)
            rrf_score = cand.get("rrf_score", 0.0)

            # Keyword match boost for meaningful domain tokens
            token_matches = sum(1 for t in query_tokens if (t in text_lower or t in section_lower))
            boost = min(0.30, token_matches * 0.06)

            # Check explicit section number matching (e.g. 'section 2.4' or 'section 4.2')
            sec_num_match = re.search(r"section\s+(\d+(?:\.\d+)?)", query_lower)
            if sec_num_match:
                req_sec = sec_num_match.group(1)
                # If section heading explicitly matches requested section number, grant strong priority
                if re.search(rf"\b{re.escape(req_sec)}\b", section_lower):
                    boost += 1.0
                elif req_sec in text_lower:
                    boost += 0.25

            # Unclipped composite score
            raw_score = 0.35 * dense_score + 0.45 * bm25_score + 0.20 * (rrf_score * 30.0) + boost

            scored_candidates.append({
                "chunk": chunk,
                "raw_score": raw_score
            })

        # Sort descending by raw unclipped score
        scored_candidates.sort(key=lambda x: x["raw_score"], reverse=True)
        top_selected = scored_candidates[:top_k]

        max_raw = max((x["raw_score"] for x in top_selected), default=1.0)
        max_raw = max(max_raw, 1.0)

        final_chunks = []
        for item in top_selected:
            c = item["chunk"]
            norm_score = round(min(1.0, item["raw_score"] / max_raw), 4)
            final_chunks.append(RetrievedChunk(
                chunk_id=c["chunk_id"],
                source=c["source"],
                page=c["page"],
                section=c["section"],
                text=c["text"],
                score=norm_score
            ))

        return final_chunks

    def retrieve(self, query: str, top_k: int = 4) -> List[RetrievedChunk]:
        """
        Hybrid retrieval workflow:
        1. Dense retrieval (top 8)
        2. Sparse BM25 retrieval (top 8)
        3. Reciprocal Rank Fusion (RRF) merge
        4. Rerank down to top_k
        """
        dense_results = self._dense_search(query, n_results=settings.TOP_CANDIDATES)
        sparse_results = self._sparse_search(query, n_results=settings.TOP_CANDIDATES)

        # Track candidate scores
        candidates_map: Dict[str, Dict[str, Any]] = {}
        rrf_k = 60.0

        for rank, (cid, sim) in enumerate(dense_results):
            if cid not in candidates_map:
                candidates_map[cid] = {"chunk": self.chunk_map[cid], "dense_score": sim, "bm25_score": 0.0, "rrf_score": 0.0}
            candidates_map[cid]["dense_score"] = sim
            candidates_map[cid]["rrf_score"] += 1.0 / (rrf_k + rank + 1)

        for rank, (cid, score) in enumerate(sparse_results):
            if cid not in candidates_map:
                candidates_map[cid] = {"chunk": self.chunk_map[cid], "dense_score": 0.0, "bm25_score": score, "rrf_score": 0.0}
            candidates_map[cid]["bm25_score"] = score
            candidates_map[cid]["rrf_score"] += 1.0 / (rrf_k + rank + 1)

        all_candidates = list(candidates_map.values())
        if not all_candidates:
            return []

        # Sort by RRF score to select top candidates before reranking
        all_candidates.sort(key=lambda x: x["rrf_score"], reverse=True)
        top_candidates = all_candidates[:settings.TOP_CANDIDATES]

        # Rerank down to top_k
        return self._rerank(top_candidates, query, top_k=top_k)
