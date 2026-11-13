import hashlib
import math
import os
import re
from typing import List
import numpy as np

try:
    from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
except ImportError:
    Documents = List[str]
    Embeddings = List[List[float]]
    EmbeddingFunction = object

from api.config import settings


class DeterministicEmbeddingFunction(EmbeddingFunction):
    """
    Lightweight deterministic hashing embedding function (dimension 512).
    Used for offline testing, local unit tests, and fallback when no hosted API key is configured.
    Zero external heavy dependencies (no PyTorch, no HuggingFace, no sentence-transformers).
    """
    def __init__(self, dimension: int = 512):
        self.dimension = dimension

    def name(self) -> str:
        return "deterministic_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        results: Embeddings = []
        for text in input:
            vec = np.zeros(self.dimension, dtype=np.float32)
            # Tokenize words and character 3-grams
            tokens = re.findall(r"\w+", text.lower())
            if not tokens:
                results.append(vec.tolist())
                continue

            for t in tokens:
                h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimension
                sign = 1.0 if (h // self.dimension) % 2 == 0 else -1.0
                vec[idx] += sign

            # Add n-grams for typo robustness
            for i in range(len(text) - 2):
                ngram = text[i:i+3].lower()
                h = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest(), 16)
                idx = h % self.dimension
                sign = 1.0 if (h // self.dimension) % 2 == 0 else -1.0
                vec[idx] += 0.5 * sign

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            results.append(vec.tolist())
        return results


class OpenAIEmbeddingFunction(EmbeddingFunction):
    """Hosted OpenAI embeddings (text-embedding-3-small)."""
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def name(self) -> str:
        return "openai_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        response = self.client.embeddings.create(
            input=input,
            model=self.model
        )
        return [item.embedding for item in response.data]


class VoyageEmbeddingFunction(EmbeddingFunction):
    """Hosted Voyage AI embeddings."""
    def __init__(self, api_key: str, model: str = "voyage-3-lite"):
        try:
            import voyageai
            self.client = voyageai.Client(api_key=api_key)
        except ImportError:
            raise ImportError("Please install voyageai to use Voyage embeddings.")
        self.model = model

    def name(self) -> str:
        return "voyage_embedding"

    def __call__(self, input: Documents) -> Embeddings:
        result = self.client.embed(texts=input, model=self.model)
        return result.embeddings


def get_embedding_function():
    provider = settings.EMBEDDING_PROVIDER.lower()
    openai_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "")
    voyage_key = settings.VOYAGE_API_KEY or os.environ.get("VOYAGE_API_KEY", "")

    if provider == "openai" and openai_key:
        return OpenAIEmbeddingFunction(api_key=openai_key, model=settings.OPENAI_EMBEDDING_MODEL)
    elif provider == "voyage" and voyage_key:
        return VoyageEmbeddingFunction(api_key=voyage_key, model=settings.VOYAGE_EMBEDDING_MODEL)
    elif openai_key:
        return OpenAIEmbeddingFunction(api_key=openai_key, model=settings.OPENAI_EMBEDDING_MODEL)
    elif voyage_key:
        return VoyageEmbeddingFunction(api_key=voyage_key, model=settings.VOYAGE_EMBEDDING_MODEL)
    else:
        # Fallback for offline / CI / testing environments without live API credentials
        return DeterministicEmbeddingFunction()
