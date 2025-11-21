from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ColumnElement,
    DateTime,
    Enum as PgEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class StatusEnum(str, Enum):
    active = "active"
    disabled = "disabled"


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[StatusEnum] = mapped_column(PgEnum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    images: Mapped[List["Image"]] = relationship(back_populates="uploader_admin")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(PgEnum(StatusEnum), default=StatusEnum.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    extended_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    assignments: Mapped[List["UserImage"]] = relationship(back_populates="user")


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bucket: Mapped[str] = mapped_column(String(128), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(128))
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(128))
    uploader_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    uploader_admin: Mapped[Optional[Admin]] = relationship(back_populates="images")
    assignments: Mapped[List["UserImage"]] = relationship(back_populates="image")

    __table_args__ = (UniqueConstraint("bucket", "key", name="uq_image_bucket_key"),)


class UserImage(Base):
    __tablename__ = "user_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    granted_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"))
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="assignments")
    image: Mapped[Image] = relationship(back_populates="assignments")
    granted_by_admin: Mapped[Optional[Admin]] = relationship()

    __table_args__ = (UniqueConstraint("user_id", "image_id", name="uq_user_image"),)


class UserExtension(Base):
    __tablename__ = "user_extensions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    old_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    new_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reason: Mapped[Optional[str]] = mapped_column(Text)
    operated_by_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship()
    admin: Mapped[Optional[Admin]] = relationship()


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(128))
    ip: Mapped[Optional[str]] = mapped_column(String(64))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[Optional[User]] = relationship()
    admin: Mapped[Optional[Admin]] = relationship()
