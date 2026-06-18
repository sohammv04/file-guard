from __future__ import annotations

import hashlib
from pathlib import Path

from .config import SUPPORTED_HASH_ALGORITHMS


def hash_file(path: Path, algorithm: str) -> str:
    normalized_algorithm = algorithm.lower()
    if normalized_algorithm not in SUPPORTED_HASH_ALGORITHMS:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher = hashlib.new(normalized_algorithm)
    with path.open("rb") as file_handle:
        while chunk := file_handle.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
