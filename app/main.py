import uvicorn, logging

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware import Middleware

from datetime import datetime

from core.middlewares import DDoSMiddlewareAPP
from core.config import APPConfig


app_config = APPConfig()

# Temporary origins
ALLOW_ORIGINS = ["*"]
ALLOWED_METHODS = ["GET", "HEAD", "OPTIONS", "PUT", "POST"]
ALLOW_HEADERS = ["*"]

middlewares = [
    Middleware(DDoSMiddlewareAPP),
    Middleware(GZipMiddleware),
    Middleware(CORSMiddleware),
    Middleware(WSGIMiddleware),
    Middleware(CORSMiddleware, 
               allow_origins=ALLOW_ORIGINS,
               allow_credentials=True,
               allow_methods=ALLOWED_METHODS,
               allow_headers=ALLOW_HEADERS,
               expose_headers=["Authorization", "Content-Type", "XMLHttpRequest", "X-SESSION-CONTENTS"])
]

api_app = FastAPI(
    title=app_config.APP_APINAME,
    description=app_config.APP_API_DESC,
    version=app_config.API_VERSION,
    middleware=middlewares
)


