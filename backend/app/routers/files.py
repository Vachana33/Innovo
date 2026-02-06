from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import User
from app.schemas import FileUploadResponse
from app.storage.file_service import get_or_create_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Protected upload endpoint.
    - Receives multipart file
    - Dedups by SHA-256
    - Uploads to Supabase Storage only once
    """
    file_bytes = await file.read()

    result = get_or_create_file(
        db,
        file_bytes=file_bytes,
        file_type=file_type,
        filename=file.filename,
    )

    return FileUploadResponse(
        file_id=result.file.id,
        content_hash=result.file.content_hash,
        file_type=result.file.file_type,
        storage_path=result.file.storage_path,
        size_bytes=result.file.size_bytes,
        mime_type=result.file.mime_type,
        original_filename=result.file.original_filename,
        reused=not result.is_new,
    )
