from sqlalchemy.orm import Session
from typing import Tuple
from fastapi import HTTPException
from typing import Optional

from app.models import File
from app.storage.file_hash import compute_file_hash
from app.storage.supabase_client import get_supabase_client
import os

BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "files")


def get_or_create_file(
    db: Session,
    file_bytes: bytes,
    mime_type: str,
    original_filename: Optional[str] = None
) -> Tuple[File, bool]:
    """
    GLOBAL FILE INGESTION SPINE
    """

    content_hash = compute_file_hash(file_bytes)
    size_bytes = len(file_bytes)

    existing = db.query(File).filter(File.content_hash == content_hash).first()
    if existing:
        return existing, False

    # Derive file_type from mime_type
    if mime_type.startswith("audio/"):
        file_type = "audio"
    elif mime_type == "application/pdf":
        file_type = "pdf"
    elif mime_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        file_type = "docx"
    else:
        file_type = "binary"

    prefix = content_hash[:2]
    storage_path = f"{file_type}/{prefix}/{content_hash}"

    supabase = get_supabase_client()
    supabase.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": mime_type},
    )

    new_file = File(
        content_hash=content_hash,
        file_type=file_type,
        mime_type=mime_type,
        storage_path=storage_path,
        size_bytes=size_bytes,
        original_filename=original_filename,
    )

    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file, True
