import uuid, jwt, argon2

from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from fastapi import Depends

from typing import Optional, Annotated, Dict
from jose import jwt, JWTError
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from argon2 import PasswordHasher, exceptions
from datetime import datetime, timedelta

# load configuration
from core.config import APIConfiguration
from core.middlewares import CustomOAuth2Middleware

api_config = APIConfiguration()
security_hasher = PasswordHasher(hash_len=64) # Argon2 Hasher
oauth2_schemes = CustomOAuth2Middleware(tokenUrl=api_config.HEADERS_DEFAULT_PATH)

# Password hashing and verification
def create_hashed_password(plain_password: str) -> str:
    """Securely hash a password using Argon2"""
    if not plain_password or len(plain_password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    try:
        return security_hasher.hash(plain_password)
    except argon2.exceptions.HashingError as e:
        raise ValueError(f"Password hashing failed: {str(e)}")


def verify_hashed_password(input_password: str, hashed_password: str) -> bool:
    """Verify a password against its Argon2 hash"""
    try:
        security_hasher.verify(hashed_password, input_password)
        
        # Check if rehash is needed (if parameters have changed)
        if security_hasher.check_needs_rehash(hashed_password):
            return False
            
        return True
    except argon2.exceptions.InvalidHashError:
        return False
    except argon2.exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        raise ValueError(f"Password verification error: {str(e)}")
# End of it

# Token Generator
def _generate_token(payload: Dict[str, str], secret_key: str = "", algorithm: str = "", expires_delta: timedelta = timedelta, subject: Optional[str] = None) -> str:
    now = datetime.now()
    try:
        exp_timestamp = int((now + expires_delta).replace(tzinfo=None).timestamp())
    except OSError:
        exp_timestamp = int((now + timedelta(days=7)).timestamp())


    payload_toencrypt = {
        **payload, # ensure all values are string
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": exp_timestamp,
        "jti": str(uuid.uuid4())
    }

    if subject: 
        payload_toencrypt["sub"] =  str(subject)

    return jwt.encode(payload_toencrypt, secret_key, algorithm=algorithm)

# Access Token & Refresh TOken 
async def create_access_token(payload: Dict[str, str], subject: Optional[str] = None) -> str:
    return _generate_token(payload=payload, secret_key=api_config.API_SECRET_KEY, algorithm=api_config.API_ALGORITHM, expires_delta=timedelta(minutes=int(api_config.API_ACCESS_EXPIRES_MINUTES)))

async def create_refresh_token(payload: Dict[str, str], subkect: Optional[str] = None) -> str:
    return _generate_token(payload=payload, secret_key=api_config.API_REFRESH_SECRETKEY, algorithm=api_config.API_ALGORITHM, expires_delta=timedelta(days=int(api_config.API_REFRESH_EXPIRES_DAYS)))

# Verify Access & Refresh Token 
def _verify_token(token: str, secret_key: str, algorithm: str) -> Dict:
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=algorithm)
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token Has expires")
    except InvalidSignatureError:
        raise ValueError("Invalid token signature")
    except InvalidTokenError:
        raise ValueError("Invalid Token error")
    
def verify_access_token(token: str) -> Dict:
    return _verify_token(token=token, secret_key=api_config.API_SECRET_KEY, algorithm=api_config.API_ALGORITHM)

def verify_refresh_token(token: str) -> Dict:
    return _verify_token(token=token, secret_key=api_config.API_REFRESH_SECRETKEY, algorithm=api_config.API_ALGORITHM)