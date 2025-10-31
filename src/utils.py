# utils.py
import json
import hashlib
from typing import Any

def _to_serializable(obj: Any):
    """Helper to convert pydantic/BaseModel or dataclass-like objects to dict for JSON."""
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return obj

def hash_data(data: Any) -> str:
    """
    Deterministic hashing of JSON-serializable structures.
    """
    try:
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, sort_keys=True, default=_to_serializable)
    except Exception:
        # Fallback: str()
        text = str(data)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def is_valid_proof(hash_hex: str, difficulty: int) -> bool:
    """Check whether hash_hex has `difficulty` leading zeros."""
    return hash_hex.startswith('0' * difficulty)
