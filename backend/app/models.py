from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func


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
