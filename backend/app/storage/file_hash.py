import hashlib


def sha256_hex(data: bytes) -> str:
    """
    Compute SHA-256 hash (hex string) for file content.
    This is our dedup "fingerprint".
    """
    return hashlib.sha256(data).hexdigest()
