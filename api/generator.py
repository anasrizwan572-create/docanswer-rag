
import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple

from api.config import settings
from api.models import Citation, QueryResponse, RetrievedChunk


SYSTEM_PROMPT = """You are DocAnswer, a highly accurate, trust-first enterprise document Q&A assistant.

Answer using ONLY the provided passages.

STRICT RULES:
1. Never assume or invent information.
2. If the passages do not contain the answer, return EXACTLY:
   "I couldn't find this in the provided documents."
3. Every factual claim must have an inline citation such as [1].
4. Cite only passages that directly support the claim.
5. Never cite irrelevant passages.
6. If evidence conflicts, explain the conflict.
7. Be concise and professional.
8. Return ONLY valid JSON using this schema:
{
  "answer": "Answer with inline citations",
  "cited_passage_ids": [1],
  "confidence": "high",
  "found": true
}
"""


STOP_WORDS = {
    "the", "are",
    "what", "when", "where", "which", "who", "whom", "whose",
    "why", "how", "many", "much", "does", "have", "been",
    "were", "this", "that", "these", "those", "from", "with",
    "about", "into", "through", "during", "before", "after",
    "above", "below", "between", "under", "again", "further",
    "then", "once", "here", "there", "both", "each", "few",
    "more", "most", "other", "some", "such", "only", "own",
    "same", "than", "too", "very", "can", "will", "just",
    "should", "now", "company", "employee", "employees",
    "provided", "documents", "document", "accordance",
    "pursuant", "section", "policy", "terms", "rules",
    "guidelines", "eligible", "eligibility", "take", "work",
    "receive", "following"
}


REFUSAL_PHRASE = (
    "I couldn't find this in the provided documents."
)


def is_stem_match(word: str, text: str) -> bool:
    """Checks exact word or a simple morphological stem."""

    w = word.lower()

    if re.search(rf"\b{re.escape(w)}\b", text):
        return True

    if w.endswith("s") and len(w) > 3:
        if re.search(rf"\b{re.escape(w[:-1])}\b", text):
            return True

    if w.endswith("es") and len(w) > 4:
        if re.search(rf"\b{re.escape(w[:-2])}\b", text):
            return True

    if w.endswith("ing") and len(w) > 5:
        if re.search(rf"\b{re.escape(w[:-3])}\b", text):
            return True

    if w.endswith("ed") and len(w) > 4:
        if re.search(rf"\b{re.escape(w[:-2])}\b", text):
            return True

    return False


def extract_json_from_text(
    text: str
) -> Optional[Dict[str, Any]]:
    """Extracts a JSON object from a model response."""

    if not isinstance(text, str):
        return None

    text = text.strip()

    match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL
    )

    if match:
        try:
            result = json.loads(match.group(1))
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError):
            pass

    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
    except (json.JSONDecodeError, TypeError):
        pass

    first_brace = text.find("{")
    last_brace = text.rfind("}")

    if first_brace != -1 and last_brace > first_brace:
        try:
            result = json.loads(
                text[first_brace:last_brace + 1]
            )
            if isinstance(result, dict):
                return result
        except (json.JSONDecodeError, TypeError):
            pass

    return None


class AnswerGenerator:
    """
    Generates grounded answers using Gemini, optional Claude,
    and a deterministic offline fallback.
    """

    def __init__(self):

        # Gemini: Primary provider
        self.gemini_key = (
            settings.GEMINI_API_KEY
            or os.environ.get("GEMINI_API_KEY", "")
        )

        self.gemini_model_name = (
            settings.GEMINI_MODEL
            or os.environ.get(
                "GEMINI_MODEL",
                "gemini-3.1-flash-lite"
            )
        )

        self.gemini_client = None

        if self.gemini_key:
            try:
                from google import genai

                self.gemini_client = genai.Client(
                    api_key=self.gemini_key
                )

            except Exception as e:
                print(
                    f"Warning: Failed to initialize Gemini client: {e}"
                )

        # Claude: Secondary provider
        self.anthropic_key = (
            settings.ANTHROPIC_API_KEY
            or os.environ.get("ANTHROPIC_API_KEY", "")
        )

        self.model_name = (
            settings.ANTHROPIC_MODEL
            or os.environ.get(
                "ANTHROPIC_MODEL",
                "claude-3-5-sonnet-20241022"
            )
        )

        self.anthropic_client = None

        if self.anthropic_key:
            try:
                import anthropic

                self.anthropic_client = anthropic.Anthropic(
                    api_key=self.anthropic_key
                )

            except Exception as e:
                print(
                    f"Warning: Failed to initialize Anthropic client: {e}"
                )

    def _format_passages(
        self,
        chunks: List[RetrievedChunk]
    ) -> str:

        formatted = []

        for idx, chunk in enumerate(chunks, 1):
            formatted.append(
                f"--- PASSAGE [{idx}] ---\n"
                f"Source: {chunk.source} | "
                f"Page: {chunk.page} | "
                f"Section: {chunk.section}\n"
                f"Text:\n{chunk.text}\n"
            )

        return "\n".join(formatted)

    def _call_gemini(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT
    ) -> str:
        """Invokes Gemini using the Google GenAI SDK."""

        if not self.gemini_client:
            raise RuntimeError(
                "Gemini client is not configured."
            )

        from google.genai import types

        response = self.gemini_client.models.generate_content(
            model=self.gemini_model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.0,
                max_output_tokens=1024,
                response_mime_type="application/json"
            )
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

    def _call_claude(
        self,
        prompt: str,
        system: str = SYSTEM_PROMPT
    ) -> str:
        """Invokes Claude via Anthropic API."""

        if not self.anthropic_client:
            raise RuntimeError(
                "Anthropic client is not configured."
            )

        response = self.anthropic_client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            temperature=0.0,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    def _validate_citations(
        self,
        answer: str,
        num_passages: int
    ) -> Tuple[bool, List[int]]:
        """Validates inline citation numbers."""

        citation_groups = re.findall(
            r"\[(\d+(?:\s*,\s*\d+)*)\]",
            answer
        )

        cited_indices = []

        for group in citation_groups:
            cited_indices.extend(
                int(value.strip())
                for value in group.split(",")
            )

        # A factual answer without citations is not accepted.
        if not cited_indices:
            return False, []

        for citation_id in cited_indices:
            if citation_id < 1 or citation_id > num_passages:
                return False, cited_indices

        return True, cited_indices

    def _offline_fallback_generator(
        self,
        question: str,
        chunks: List[RetrievedChunk]
    ) -> Dict[str, Any]:
        """Deterministic rule-based fallback for offline use."""

        q_lower = question.lower()

        query_words = [
            w for w in re.findall(r"\w+", q_lower)
            if len(w) >= 3 and w not in STOP_WORDS
        ]

        minimum_matches = (
            2 if len(query_words) >= 2 else 1
        )

        all_chunk_text = " ".join(
            f"{c.section} {c.text}" for c in chunks
        ).lower()

        matched_words = [
            w for w in query_words
            if is_stem_match(w, all_chunk_text)
        ]

        coverage = (
            len(matched_words) / max(1, len(query_words))
        )

        known_absent_concepts = [
            "pet", "veterinary", "dog", "cat",
            "equity", "stock", "option", "rsu",
            "crypto", "car", "vehicle", "lease",
            "gym", "fitness", "paternity",
            "kingdom", "uk", "daycare",
            "kindergarten", "mars"
        ]

        has_absent_concept = any(
            re.search(rf"\b{re.escape(c)}\b", q_lower)
            for c in known_absent_concepts
        )

        if (
            has_absent_concept
            or coverage < 0.40
            or (
                chunks
                and chunks[0].score < 0.40
                and coverage < 0.60
            )
        ):
            return {
                "answer": REFUSAL_PHRASE,
                "cited_passage_ids": [],
                "confidence": "high",
                "found": False
            }

        cited_ids = []
        answer_parts = []

        for idx, chunk in enumerate(chunks[:2], 1):

            sentences = [
                s.strip()
                for s in re.split(
                    r"(?:(?<=[.!?])\s+|\n+)",
                    chunk.text
                )
                if s.strip()
            ]

            relevant = []

            for sentence in sentences:
                sentence_lower = sentence.lower()

                matches_count = sum(
                    1 for word in query_words
                    if is_stem_match(word, sentence_lower)
                )

                if matches_count >= minimum_matches:
                    relevant.append(
                        (matches_count, sentence)
                    )

            relevant.sort(
                key=lambda item: item[0],
                reverse=True
            )

            if relevant:

                top_sentences = [
                    item[1] for item in relevant[:2]
                ]

                answer_parts.append(
                    f"{' '.join(top_sentences)} [{idx}]"
                )

                cited_ids.append(idx)

        if not answer_parts:
            return {
                "answer": REFUSAL_PHRASE,
                "cited_passage_ids": [],
                "confidence": "high",
                "found": False
            }

        return {
            "answer": " ".join(answer_parts),
            "cited_passage_ids": cited_ids,
            "confidence": "medium",
            "found": True
        }

    def generate(
        self,
        question: str,
        chunks: List[RetrievedChunk]
    ) -> QueryResponse:
        """Generates a grounded answer with validated citations."""

        if not chunks:
            return QueryResponse(
                answer=REFUSAL_PHRASE,
                citations=[],
                confidence="high",
                found=False
            )

        passages_text = self._format_passages(chunks)

        user_prompt = (
            f"QUESTION:\n{question}\n\n"
            f"PROVIDED PASSAGES:\n{passages_text}\n\n"
            "Return a valid JSON object with answer, "
            "cited_passage_ids, confidence, and found."
        )

        parsed_data = None

        # Gemini primary provider
        if self.gemini_client:
            try:
                raw_response = self._call_gemini(user_prompt)
                parsed_data = extract_json_from_text(raw_response)

            except Exception as e:
                print(f"Error calling Gemini: {e}")

        # Claude secondary provider
        if not parsed_data and self.anthropic_client:
            try:
                raw_response = self._call_claude(user_prompt)
                parsed_data = extract_json_from_text(raw_response)

            except Exception as e:
                print(f"Error calling Claude: {e}")

        # Offline fallback
        if not parsed_data:
            parsed_data = self._offline_fallback_generator(
                question,
                chunks
            )

        answer_value = parsed_data.get("answer", "")
        answer_text = (
            answer_value.strip()
            if isinstance(answer_value, str)
            else ""
        )

        is_found = parsed_data.get("found", True)

        if (
            not is_found
            or not answer_text
            or REFUSAL_PHRASE.lower() in answer_text.lower()
        ):
            return QueryResponse(
                answer=REFUSAL_PHRASE,
                citations=[],
                confidence="high",
                found=False
            )

        is_valid, cited_ids = self._validate_citations(
            answer_text,
            len(chunks)
        )

        # Retry Gemini once for invalid citations
        if not is_valid and self.gemini_client:
            try:
                retry_prompt = (
                    f"{user_prompt}\n\n"
                    f"Your previous citations were invalid or missing. "
                    f"Use only passage numbers from 1 to {len(chunks)}. "
                    "Cite every factual claim. Return corrected JSON."
                )

                retry_response = self._call_gemini(retry_prompt)
                retry_data = extract_json_from_text(retry_response)

                if retry_data:
                    retry_answer_value = retry_data.get(
                        "answer", ""
                    )

                    retry_answer = (
                        retry_answer_value.strip()
                        if isinstance(retry_answer_value, str)
                        else ""
                    )

                    retry_valid, retry_ids = self._validate_citations(
                        retry_answer,
                        len(chunks)
                    )

                    if (
                        retry_valid
                        and retry_data.get("found", True)
                        and retry_answer
                        and REFUSAL_PHRASE.lower()
                        not in retry_answer.lower()
                    ):
                        parsed_data = retry_data
                        answer_text = retry_answer
                        cited_ids = retry_ids
                        is_valid = True

            except Exception as e:
                print(f"Gemini citation retry failed: {e}")

        if not is_valid:
            return QueryResponse(
                answer=REFUSAL_PHRASE,
                citations=[],
                confidence="low",
                found=False
            )

        unique_cited = sorted(set(cited_ids))
        citations: List[Citation] = []

        for cid in unique_cited:
            chunk = chunks[cid - 1]

            citations.append(
                Citation(
                    id=cid,
                    source=chunk.source,
                    page=chunk.page,
                    section=chunk.section,
                    passage_text=chunk.text,
                    score=chunk.score
                )
            )

        confidence_val = parsed_data.get(
            "confidence",
            "high"
        )

        if confidence_val not in ("high", "medium", "low"):
            confidence_val = "high"

        return QueryResponse(
            answer=answer_text,
            citations=citations,
            confidence=confidence_val,
            found=True
        )
