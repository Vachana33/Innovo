from pydantic import BaseModel, EmailStr, Field
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    success: bool
    message: str

class FileUploadResponse(BaseModel):
    file_id: UUID
    content_hash: str
    file_type: str
    storage_path: str
    size_bytes: int
    mime_type: str
    original_filename: Optional[str]
    reused: bool  # True if dedup reused existing file