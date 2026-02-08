from __future__ import annotations

import json
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import FundingProgram, UserTemplate
from app.templates.system_templates import SYSTEM_TEMPLATES


def resolve_template_for_funding_program(
    db: Session,
    funding_program: FundingProgram,
) -> dict:
    """
    Returns a FULL template structure with 'sections',
    regardless of system or user template.
    """

    # -------------------------
    # System templates
    # -------------------------
    if funding_program.template_source == "system":
        template_fn = SYSTEM_TEMPLATES.get(funding_program.template_ref)

        if not template_fn:
            raise HTTPException(
                status_code=500,
                detail=f"Unknown system template '{funding_program.template_ref}'",
            )

        # Call the registered system template function
        return template_fn()

    # -------------------------
    # User templates
    # -------------------------
    if funding_program.template_source == "user":
        template = db.query(UserTemplate).filter(
            UserTemplate.id == funding_program.template_ref
        ).first()

        if not template:
            raise HTTPException(
                status_code=404,
                detail="User template not found",
            )

        headings = json.loads(template.sections)

        sections = []
        for idx, title in enumerate(headings, start=1):
            sections.append(
                {
                    "id": str(idx),
                    "title": title,
                    "content": "",
                    "type": "text",
                }
            )

        return {"sections": sections}

    # -------------------------
    # Safety fallback
    # -------------------------
    raise HTTPException(
        status_code=500,
        detail="Invalid template_source",
    )
