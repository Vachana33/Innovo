from pydantic import BaseModel, EmailStr, Field
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from typing import List, Literal
from pydantic import BaseModel, Field


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


class FundingProgramCreate(BaseModel):
    title: str = Field(min_length=1)
    template_source: Literal["system", "user"]
    template_ref: str  # system template name OR user template UUID string


class FundingProgramResponse(BaseModel):
    id: int
    title: str
    template_source: str
    template_ref: str

    class Config:
        orm_mode = True


class FundingProgramDocumentResponse(BaseModel):
    id: int
    funding_program_id: int
    file_id: UUID
    storage_path: str
    size_bytes: int

    class Config:
        orm_mode = True
from typing import List, Optional
from uuid import UUID


class UserTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sections: List[str]


class UserTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[str]] = None


class UserTemplateResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    sections: List[str]

    class Config:
        orm_mode = True
