import uuid

from typing import Annotated, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import APPConfig, APIConfiguration
from db.session import get_db
from core.exceptions import AppException

from core.middlewares import CustomOAuth2Middleware

# Security Schemes
oauth2_schemes = CustomOAuth2Middleware(tokenUrl=f"{APPConfig.APP_API_DEFAULT_PATH}/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

class TokenPayload(BaseModel):
    sub: str # user_id
    exp: datetime
    iat: datetime
    type: str # access or refresh token 
    scopes: list[str] = []
    

async def get_current_user(request: Request, db: Annotated[AsyncSession, Depends(get_db)],
                           credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(http_bearer)],
                           token: Annotated[Optional[str], Depends(oauth2_schemes)]):
    pass