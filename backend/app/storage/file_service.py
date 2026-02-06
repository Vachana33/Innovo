from __future__ import annotations

import mimetypes
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import File as FileModel
from app.storage.file_hash import sha256_hex
from app.storage.supabase_client import get_bucket_name, get_supabase_client


@dataclass(frozen=True)
class StoredFileResult:
    file: FileModel
    is_new: bool


def _safe_ext(filename: Optional[str]) -> str:
    """
    Returns a safe extension without dot, fallback to 'bin'.
    """
    if not filename:
        return "bin"
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip(".")
    return ext if ext else "bin"


def _infer_mime(filename: Optional[str], fallback: str = "application/octet-stream") -> str:
    if not filename:
        return fallback
    mime, _ = mimetypes.guess_type(filename)
    return mime or fallback


def _build_storage_path(file_type: str, content_hash: str, filename: Optional[str]) -> str:
    """
    Stable path derived from hash.
    Example: pdf/ab/<hash>.pdf
    """
    prefix = content_hash[:2]
    ext = _safe_ext(filename)
    return f"{file_type}/{prefix}/{content_hash}.{ext}"


def get_or_create_file(
    db: Session,
    *,
    file_bytes: bytes,
    file_type: str,
    filename: Optional[str],
) -> StoredFileResult:
    """
    Global dedup rule:
      - Same content (same SHA-256) => reuse existing DB row + storage object.
      - Otherwise upload once and create DB row.

    Raises:
      - HTTPException(413) if file is too large / storage rejects payload
      - HTTPException(500) for storage failures
    """
    content_hash = sha256_hex(file_bytes)

    existing = (
        db.query(FileModel)
        .filter(FileModel.content_hash == content_hash)
        .first()
    )
    if existing:
        return StoredFileResult(file=existing, is_new=False)

    storage_path = _build_storage_path(file_type, content_hash, filename)
    mime_type = _infer_mime(filename)
    size_bytes = len(file_bytes)

    # Upload to Supabase Storage
    supabase = get_supabase_client()
    bucket = get_bucket_name()

    try:
        # If object already exists, Supabase may throw conflict; we treat it as OK.
        # We still create DB row because DB is our index.
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=file_bytes,
            file_options={"content-type": mime_type},
        )
    except Exception as e:
        msg = str(e).lower()
        # Handle 413 / payload too large from storage/proxy
        if "413" in msg or "payload too large" in msg or "too large" in msg:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large for upload.",
            )
        # Handle "already exists" style conflicts
        if "already exists" in msg or "duplicate" in msg or "conflict" in msg:
            # Treat as success; object is there.
            pass
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Storage upload failed: {str(e)}",
            )

    new_file = FileModel(
        content_hash=content_hash,
        file_type=file_type,
        storage_path=storage_path,
        size_bytes=size_bytes,
        mime_type=mime_type,
        original_filename=filename,
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return StoredFileResult(file=new_file, is_new=True)
