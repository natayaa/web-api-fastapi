from pydantic import BaseModel, EmailStr, Field

from schemas.user import UserPublic

class LoginRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str 
    token_type: str = "bearer"
    user: UserPublic

class RefreshRequest(BaseModel):
    refresh_token: str = Field(...)

class RefreshResponse(BaseModel):
    access_token: str = Field(...)
    token_type: str = "bearer"