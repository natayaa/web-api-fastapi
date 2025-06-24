from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Optional

class TokenBase(BaseModel):
    token_type: str = Field(default_factory="bearer", examples="bearer")

class TokenCreate(TokenBase):
    access_token: str = Field(..., examples="e4hpy9et9weyfdgh...")
    refresh_token: Optional[str] = Field(None, examples="9gehn9eprtjthgdilg...")

class TokenPayload(BaseModel):
    sub: str = Field(..., description="Subject (user_id)", examples="UUID tbh")
    exp: datetime = Field(..., description="Expiration time")
    jti: str = Field(..., description="TOKEN UUID", examples="937ert-394h-3874rh-..")
    type: str = Field(..., description="Token Type", examples="access/refresh")

class TokenBlacklist(BaseModel):
    """ For implementing logout """
    jti: str
    exp: datetime