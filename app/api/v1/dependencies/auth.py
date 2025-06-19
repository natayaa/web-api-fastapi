from typing import Annotated, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import APPConfig, APIConfiguration
from db.session import get_db
from core.exceptions import AppException

# Security Schemes
oauth2_schemes = OAuth2PasswordBearer(tokenUrl=f"{APPConfig.APP_API_DEFAULT_PATH}/auth/login", auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

class TokenPayload(BaseModel):
    sub: str # user_id
    exp: datetime
    iat: datetime
    type: str # access or refresh token 
    scopes: list[str] = []

# Dependencies utility
async def get_token_payload(token: str, required_scopes: Optional[list[str]] = None) -> TokenPayload:
    try:
        payload = jwt.decode(token, 
                             APIConfiguration.API_SECRET_KEY, 
                             APIConfiguration.API_ALGORITHM,
                             options={
                                 "require_sub": True,
                                 "require_exp": True,
                                 "verify_aud": False
                             }
                             )
        token_data = TokenPayload(**payload)

        # check token expiration
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise AppException.Unauthorized("Token Expired, refresh it")
        
        # check scopes if required
        if required_scopes:
            if not all(scope in token_data.scopes for scope in required_scopes):
                print(f"Insufficient permission")

        return token_data
    except (JWTError, ValidationError) as e:
        raise AppException.Unauthorized("Invalid Token") from e