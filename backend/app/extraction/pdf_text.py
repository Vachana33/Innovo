from __future__ import annotations

from typing import Optional
import io

from pypdf import PdfReader


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from a PDF (bytes).
    Returns a single combined string.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            parts.append(text)

    return "\n\n".join(parts).strip()
