from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import User
from app.schemas import FileUploadResponse
from app.storage.file_service import get_or_create_file

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Protected global file upload endpoint.
    """
    file_bytes = await file.read()

    file_obj, is_new = get_or_create_file(
        db=db,
        file_bytes=file_bytes,
        mime_type=file.content_type or "application/octet-stream",
        original_filename=file.filename,
    )

    return FileUploadResponse(
        file_id=file_obj.id,
        content_hash=file_obj.content_hash,
        file_type=file_obj.file_type,
        storage_path=file_obj.storage_path,
        size_bytes=file_obj.size_bytes,
        mime_type=file_obj.mime_type,
        original_filename=file_obj.original_filename,
        reused=not is_new,
    )
