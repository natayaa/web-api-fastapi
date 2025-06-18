import asyncio, time, re

from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from collections import defaultdict, deque
from typing import Optional
#from itsdangerous import


class DDoSMiddlewareAPP(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60, block_seconds: int = 60):
        """
            Mitigate DDoS Attack just on application layer
            better to use Redis
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.block_seconds = block_seconds
        
        self.requests = defaultdict(deque)
        self.blocked_ips = []
        self.lock = asyncio.Lock()

    async def dispatch(self, request, call_next):
        ip = request.client.host
        now = time.time()

        async with self.lock:
            # unbound ip address
            if ip in self.blocked_ips and now >= self.blocked_ips[ip]:
                del self.blocked_ips[ip]

            # if blocked
            if ip in self.blocked_ips:
                # can use the HTML or whatever you want
                # but now i only implement jsonresponse
                return JSONResponse({"detail": "Too Many Request. Try again later after 10 minutes"}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
            
            self.requests[ip].append(now)

            # remove timestamp older than window
            while self.requests[ip] and self.requests[ip][0] < now - self.window_seconds:
                self.requests[ip].popleft()

            if len(self.requests[ip]) > self.max_requests:
                self.blocked_ips[ip] = now + self.block_seconds
                return JSONResponse({"detail": "Rate Limit exceeded, your access temporary being held/ban for several minutes"}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        return await super().dispatch(request, call_next)
    


class CustomHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["Strict-Transport-Security"] = f"max-age=31536000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers['X-XSS-Protection'] = "1;mode=block;"
        response.headers['X-Frame-Options'] = "ALLOW"
        response.headers['Referrer-Policy'] = "strict-origin-when-cross-origin"
        response.headers['geolocation=(self)']
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Cache-Control'] = "no-store, no-cache, must-revalidate, proxy-revalidate"

        csp = (
            "default-src 'self';"
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self';"
        )
        
        response.headers['Content-Security-Policy'] = csp

        return response


class CustomOAuth2Middleware(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str = "", auto_err: bool = True):
        super().__init__(tokenUrl=tokenUrl, auto_error=auto_err)

    async def __call__(self, request):
        auth_header = Optional[str] = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization access, do authentication", headers={"WWW-Authenticate": "Bearer"})
        
        # validate format Bearer <token>
        match_re = re.match(r"(?i)^Bearer\s+([^\s]+)$", auth_header)
        if not match_re:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header format?", headers={"WWW-Authenticate": "Bearer"})
        
        token = match_re.group(1)


        return token