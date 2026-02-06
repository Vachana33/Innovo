import hashlib

def compute_file_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash (hex string) for file content.
    Used for deduplication.
    """
    return hashlib.sha256(data).hexdigest()
