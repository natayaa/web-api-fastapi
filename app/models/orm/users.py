from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4, UUID

from sqlalchemy import (
    String, Boolean, Integer, ForeignKey
)
from sqlalchemy import Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.orm.base import Base, TimestampMixin

class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

class IdentityType(str, Enum):
    KTP = "ktp"
    PASSPROT = "password"
    SIM = "sim"
    OTHER = "other"

class User(Base, TimestampMixin):
    __tablename__ = "tb_users"
    __table_args__ = {
        "comment": "stores system user authentication data",
        "schemas": "auth"
    }

    # primary key
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, server_default=text("gen_random_uuid()"), index=True)

    # authentication field
    username: Mapped[str] = mapped_column(String(70), nullable=False, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # business field
    point: Mapped[int] = mapped_column(Integer, default=0)
    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "tb_user_profile"

    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("tb_users.user_id", ondelete="CASCADE"), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255))
    middle_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(255))
    identity_type: Mapped[Optional[str]] = mapped_column(String(50))
    identity_number: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped["User"] = relationship(back_populates="profile")