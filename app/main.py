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
    #Middleware(DDoSMiddlewareAPP),
    Middleware(GZipMiddleware),
    Middleware(WSGIMiddleware),
    #Middleware(HTTPSRedirectMiddleware),
    # CORS middleware (carefully configured)
    Middleware(
        CORSMiddleware,
        allow_origins=ALLOW_ORIGINS,  # Should be a list of specific origins
        allow_credentials=True,
        allow_methods=ALLOWED_METHODS,  # Should be ["GET", "POST", etc.]
        allow_headers=ALLOW_HEADERS,     # Should include required headers
        expose_headers=[
            "Authorization",
            "Content-Type",
            "Content-Length",
            "X-Request-ID",
            "X-Response-Time"
        ],
        max_age=600  # 10 minutes for preflight cache
    )
]


def boot_app() -> FastAPI:
    app = FastAPI(
        title=app_config.APP_APINAME,
        version=app_config.API_VERSION,
        docs_url="/docs",
        middleware=middlewares
    )

    return app


from api.v1.endpoints.user import user_endpoint
pp = FastAPI()

pp.include_router(user_endpoint)

if __name__ == "__main__":
    uvicorn.run(
        app="main:pp",
        host="localhost",
        reload=True
    )