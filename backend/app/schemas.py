from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import StatusEnum


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class AdminBase(BaseModel):
    username: str
    is_superadmin: bool = False
    status: StatusEnum = StatusEnum.active


class AdminCreate(AdminBase):
    password: str = Field(min_length=6)


class AdminUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=6)
    status: Optional[StatusEnum] = None
    is_superadmin: Optional[bool] = None


class AdminRead(AdminBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    status: StatusEnum = StatusEnum.active
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    password: Optional[str] = Field(default=None, min_length=6)
    status: Optional[StatusEnum] = None
    expires_at: Optional[datetime] = None
    notes: Optional[str] = None


class UserExtendRequest(BaseModel):
    new_expires_at: datetime
    reason: Optional[str] = None


class UserRead(UserBase):
    id: int
    created_at: datetime
    extended_until: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImageBase(BaseModel):
    bucket: str
    key: str
    filename: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    checksum_sha256: Optional[str] = None


class ImageCreate(ImageBase):
    pass


class ImageRead(ImageBase):
    id: int
    uploader_admin_id: Optional[int] = None
    created_at: datetime
    deleted_at: Optional[datetime] = None
    assigned_count: Optional[int] = 0
    presigned_url: Optional[str] = None
    download_url: Optional[str] = None
    thumb_url: Optional[str] = None

    class Config:
        from_attributes = True


class AssignUsersRequest(BaseModel):
    user_ids: List[int]
    expires_at: Optional[datetime] = None


class AssignImagesRequest(BaseModel):
    image_ids: List[int]
    expires_at: Optional[datetime] = None


class AssignmentRead(BaseModel):
    user_id: int
    image_id: int
    granted_by_admin_id: Optional[int] = None
    granted_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsSummary(BaseModel):
    total_users: int
    active_users: int
    disabled_users: int
    expiring_users: int
    total_images: int


class UploadUrlRequest(BaseModel):
    filename: str
    content_type: Optional[str] = None
    directory: Optional[str] = None


class UploadUrlResponse(BaseModel):
    url: str
    bucket: str
    key: str
