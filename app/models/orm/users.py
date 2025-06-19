from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from orm.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "tb_users"
    __table_args__ = {"comment": "System user table"}

    user_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(70), nullable=False, index=True, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(25))
    is_active = Column(Boolean, default=True)
    point = Column(Integer(255), default=0)

    profile = relationship("UserProfile", uselist=False, back_populates="user")

class UserProfile(Base):
    __tablename__ = "tb_user_profile"

    id = Column(UUID(as_uuid=True), ForeignKey("tb_users"), primary_key=True)
    first_name = Column(String(255))
    middle_name = Column(String(255), nullable=True)
    last_name = Column(String(255))
    phone_number = Column(String(30))
    identity_type = Column(String(50))
    identity_number = Column(String(50))

    user = relationship("User", back_populates="profile")


