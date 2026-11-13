import os
import shutil
import time
from pathlib import Path
from typing import Dict
from api.config import settings

# Global timestamp cache for simple in-memory rate limiting per client IP
_rate_limit_cache: Dict[str, list] = {}


def ensure_index_ready() -> Path:
    """
    On Vercel Serverless environment, the bundle is read-only.
    Copies index from bundle /index to /tmp/index on cold start if not already copied.
    On local environments, returns settings.INDEX_DIR directly.
    """
    if os.environ.get("VERCEL"):
        target_dir = Path("/tmp/index")
        if not (target_dir / "chroma_db").exists() or not (target_dir / "bm25_index.json").exists():
            source_dir = settings.INDEX_DIR
            target_dir.mkdir(parents=True, exist_ok=True)
            if source_dir.exists():
                shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        return target_dir
    return settings.INDEX_DIR


def check_rate_limit(client_ip: str) -> bool:
    """
    Enforces sliding-window rate limit (default: 30 requests/minute).
    Returns True if allowed, False if exceeded.
    """
    now = time.time()
    window = 60.0
    limit = settings.RATE_LIMIT_PER_MINUTE

    timestamps = _rate_limit_cache.get(client_ip, [])
    # Filter timestamps within current window
    valid_timestamps = [t for t in timestamps if now - t < window]

    if len(valid_timestamps) >= limit:
        _rate_limit_cache[client_ip] = valid_timestamps
        return False

    valid_timestamps.append(now)
    _rate_limit_cache[client_ip] = valid_timestamps
    return True
