from datetime import datetime
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content_hash = Column(Text, unique=True, nullable=False, index=True)

    # Small categorization for folder structure: "audio" | "pdf" | "docx" | "text" etc.
    file_type = Column(Text, nullable=False)

    # Supabase Storage object path
    storage_path = Column(Text, nullable=False)

    # Metadata
    size_bytes = Column(Integer, nullable=False)
    mime_type = Column(Text, nullable=False)
    original_filename = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
# =========================
# Funding Program Models
# =========================

class FundingProgram(Base):
    __tablename__ = "funding_programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)

    # Template selection
    # "system" | "user"
    template_source = Column(String, nullable=False)
    # if system: template name (string); if user: UUID as string
    template_ref = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    documents = relationship("FundingProgramDocument", back_populates="funding_program", cascade="all, delete-orphan")


class FundingProgramDocument(Base):
    __tablename__ = "funding_program_documents"

    id = Column(Integer, primary_key=True, index=True)

    funding_program_id = Column(Integer, ForeignKey("funding_programs.id"), nullable=False, index=True)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id"), nullable=False, index=True)

    # Extracted rules text (from the guideline PDF)
    extracted_text = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    funding_program = relationship("FundingProgram", back_populates="documents")
    file = relationship("File")


class UserTemplate(Base):
    __tablename__ = "user_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Stored as JSON-encoded list of headings
    sections = Column(Text, nullable=False)

    # Who created the template
    user_email = Column(String, ForeignKey("users.email"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
