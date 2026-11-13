import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base paths
    ROOT_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = ROOT_DIR / "data"
    INDEX_DIR: Path = ROOT_DIR / "index"
    RUNTIME_INDEX_DIR: Path = Path("/tmp/index") if os.environ.get("VERCEL") else (ROOT_DIR / "index")

    # LLM Settings
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    # Embeddings Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")  # "openai", "voyage", "deterministic"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    VOYAGE_API_KEY: str = os.getenv("VOYAGE_API_KEY", "")
    VOYAGE_EMBEDDING_MODEL: str = os.getenv("VOYAGE_EMBEDDING_MODEL", "voyage-3-lite")

    # Security & Rate Limiting
    MAX_QUESTION_LENGTH: int = 500
    RATE_LIMIT_PER_MINUTE: int = 30

    # Retrieval parameters
    TOP_CANDIDATES: int = 8
    TOP_RERANKED: int = 4

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
