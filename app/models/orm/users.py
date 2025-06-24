from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, Integer, ForeignKey, Enum as SQLEnum, text
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
    PASSPORT = "passport"  # Fixed typo from "password"
    SIM = "sim"
    OTHER = "other"

class User(Base, TimestampMixin):
    __tablename__ = "tb_users"
    __table_args__ = {
        "comment": "Stores system user authentication data",
        "schema": "auth"  # Fixed typo from "schemas"
    }

    # Primary Key
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
        index=True
    )

    # Authentication Fields
    username: Mapped[str] = mapped_column(
        String(70),
        nullable=False,
        index=True,
        unique=True,
        comment="Alphanumeric and underscores only"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="BCrypt hashed password"
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Must be a valid email address"
    )

    # Authorization
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        comment="User's permission level"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="Soft delete flag"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="Email verification status"
    )

    # Business Field
    point: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Loyalty or reward points"
    )

    # Security Tracking
    last_login: Mapped[Optional[datetime]] = mapped_column(
        comment="Timestamp of last successful login"
    )
    failed_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Consecutive failed login attempts"
    )

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

class UserProfile(Base):
    __tablename__ = "tb_user_profile"
    __table_args__ = {"comment": "Stores additional user profile data"}

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("auth.tb_users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Given name"
    )
    middle_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Middle name or patronymic"
    )
    last_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Family name"
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20),  # Reduced from 255 to match E.164 standard
        comment="E.164 formatted phone number"
    )
    identity_type: Mapped[Optional[IdentityType]] = mapped_column(
        SQLEnum(IdentityType),
        comment="Government ID type"
    )
    identity_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="ID document number"
    )
    metadata_: Mapped[Optional[dict]] = mapped_column(
        "metadata",
        JSONB,
        comment="Additional unstructured profile data"
    )

    user: Mapped["User"] = relationship(back_populates="profile")