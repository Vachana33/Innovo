from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import User, FundingProgram, FundingProgramDocument
from app.schemas import FundingProgramCreate, FundingProgramResponse, FundingProgramDocumentResponse
from app.storage.file_service import get_or_create_file
from app.extraction.pdf_text import extract_text_from_pdf_bytes

router = APIRouter(prefix="/funding-programs", tags=["funding-programs"])


@router.post("", response_model=FundingProgramResponse)
def create_funding_program(
    payload: FundingProgramCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Global funding programs: do NOT filter by user
    fp = FundingProgram(
        title=payload.title,
        template_source=payload.template_source,
        template_ref=payload.template_ref,
    )
    db.add(fp)
    db.commit()
    db.refresh(fp)
    return fp


@router.get("", response_model=List[FundingProgramResponse])
def list_funding_programs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Global view for internal users
    return db.query(FundingProgram).order_by(FundingProgram.created_at.desc()).all()


@router.post("/{funding_program_id}/guidelines/upload", response_model=List[FundingProgramDocumentResponse])
async def upload_guidelines(
    funding_program_id: int,
    files: List[UploadFile] = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fp = db.query(FundingProgram).filter(FundingProgram.id == funding_program_id).first()
    if not fp:
        raise HTTPException(status_code=404, detail="Funding program not found")

    responses: list[FundingProgramDocumentResponse] = []

    for upload in files:
        if upload.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"Only PDF allowed. Got: {upload.content_type}")

        pdf_bytes = await upload.read()

        # spine rule: always go through get_or_create_file()
        file_obj, _is_new = get_or_create_file(
            db=db,
            file_bytes=pdf_bytes,
            mime_type=upload.content_type or "application/pdf",
            original_filename=upload.filename,
        )

        extracted_text = extract_text_from_pdf_bytes(pdf_bytes)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail=f"Could not extract text from PDF: {upload.filename}")

        doc = FundingProgramDocument(
            funding_program_id=fp.id,
            file_id=file_obj.id,
            extracted_text=extracted_text,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        responses.append(
            FundingProgramDocumentResponse(
                id=doc.id,
                funding_program_id=doc.funding_program_id,
                file_id=file_obj.id,
                storage_path=file_obj.storage_path,
                size_bytes=file_obj.size_bytes,
            )
        )

    return responses
