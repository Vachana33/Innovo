import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import User, UserTemplate
from app.schemas import (
    UserTemplateCreate,
    UserTemplateUpdate,
    UserTemplateResponse,
)
from app.templates.system_templates import SYSTEM_TEMPLATES

router = APIRouter(prefix="/templates", tags=["templates"])
@router.post("/user", response_model=UserTemplateResponse, status_code=201)
def create_user_template(
    payload: UserTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.sections:
        raise HTTPException(400, "Template must have at least one section")

    template = UserTemplate(
        name=payload.name.strip(),
        description=payload.description,
        sections=json.dumps(payload.sections),
        user_email=current_user.email,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return UserTemplateResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        sections=payload.sections,
    )

@router.get("/list")
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_templates = db.query(UserTemplate).filter(
        UserTemplate.user_email == current_user.email
    ).all()

    return {
        "system": [
            {"id": name, "name": name, "source": "system"}
            for name in SYSTEM_TEMPLATES.keys()
        ],
        "user": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "source": "user",
            }
            for t in user_templates
        ],
    }
