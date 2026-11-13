from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

class QueryRequest(BaseModel):
    question: str = Field(..., description="The user question about the document")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty.")
        if len(cleaned) > 500:
            raise ValueError(f"Question exceeds max length of 500 characters (length: {len(cleaned)}).")
        return cleaned


class Citation(BaseModel):
    id: int = Field(..., description="Citation index corresponding to [1], [2], etc.")
    source: str = Field(..., description="Source filename")
    page: int = Field(..., description="1-based page number")
    section: str = Field(..., description="Document section heading")
    passage_text: str = Field(..., description="Exact text excerpt of the passage")
    score: float = Field(..., description="Retrieval / relevance score")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Synthesized answer with inline citations or standard refusal")
    citations: List[Citation] = Field(default_factory=list, description="Passages cited in the answer")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level")
    found: bool = Field(..., description="True if answer found in documents, False if refused/not found")


class RetrievedChunk(BaseModel):
    chunk_id: str
    source: str
    page: int
    section: str
    text: str
    score: float = 0.0
