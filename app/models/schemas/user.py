from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic import model_validator
from typing import Optional
from enum import Enum
from datetime import datetime

import re

class UserRole(str, Enum):
    ADMIN: str = "admin"
    USER: str = "user"
    GUEST: str = "guest"
    MODERATOR: str = "moderator"

class RestrictedUsernames(str, Enum):
    ADMIN = "admin"
    ROOT = "root"
    SYSTEM = "system"
    SUPPORT = "support"

class UserBase(BaseModel):
    email: EmailStr = Field(..., examples="something@gmail.com", description="Must be a valid email address")
    username: str = Field(..., min_length=4, max_length=40, pattern=r"^[a-zA-Z0-9_]+$")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50)
    password_confirm: str = Field(..., description="Must match password")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v_lower = v.lower()
        for reserved in RestrictedUsernames:
            if v_lower == reserved.value:
                raise ValueError(f"Username : '{v}' is restricted")
            
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        forbidden_patterns = [
            r"[\'\";]", # sql injection trigger
            r"[<>]", # XML
            r"\s", # Whitespace
            r"[\\\/]", # path traversal
            r"[\{\}\[\]\(\)]", # code block injection
            r"(?i)(select|insert|delete|drop|alter|create|exec)", # SQL keywords
            r"(?i)(union|join|having|where)",
            r"(?i)(script|alert|onerror|onload)",
            r"\.\.\/", # directory traversal
        ]
        # check length
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 50:
            raise ValueError("Password length can't be more than 50 characters")
        
        # check forbidden characters
        for pattern in forbidden_patterns:
            if re.search(pattern, v):
                raise ValueError(f"Password contains invalid characters/pattersn: {pattern}")

        requirements = [
            r"[A-Z]",
            r"[a-z]",
            r"[0-9]",
            r"[!@#$%^&*]", # Allowed special characters
        ]
        met = sum(bool(re.search(req, v)) for req in requirements)
        if met < 3:
            raise ValueError("Password must contain at least 3 of : uppercase, lowercase or special characters")
        
        return v
    
    @model_validator(mode="after")
    def validate_password_match(self) -> "UserCreate":
        if self.password != self.password_confirm:
            raise ValueError("Password doesn't match")
        return self
    


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(...)
    username: Optional[str] = Field(...)
    current_password: Optional[str] = Field(None, description="Required when changing sensitive field")
    new_password: Optional[str] = Field(None, min_length=8, max_length=50)

    @model_validator(mode="after")
    def validate_password_change(self) -> "UserUpdate":
        sensitive_fields = ["email", "username", "new_password"]
        if any(getattr(self, field) is not None for field in sensitive_fields):
            if not self.current_password:
                raise ValueError("Current password required for changes")
            
        return self


class UserInDB(UserBase):
    user_id: str = Field(..., alias="user_id")
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)

    class Config:
        from_attributes = True
        populate_by_name = True


class UserPublic(UserInDB):
    """Public user representation without sensitive data """
    pass

class UserPrivate(UserInDB):
    hashed_password: str = Field(..., example="actually hashed password")
    last_login: Optional[datetime] = Field(None, description="Timestamp of last successfull login attemp")
    failed_attemps: int = Field(default=0, description="Consecutive failed login attemps")
    