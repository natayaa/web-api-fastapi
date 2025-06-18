import uuid, jwt

from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from fastapi import Depends

from typing import Optional, Annotated, Dict
from jose import jwt, JWTError
from itsdangerous import URLSafeSerializer, BadSignature, SignatureExpired
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError

# load configuration
from core.config import APIConfiguration

api_config = APIConfiguration()
