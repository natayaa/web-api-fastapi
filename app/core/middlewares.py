import asyncio, time, re

from fastapi.security import OAuth2PasswordBearer
from starlette import status
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from collections import defaultdict, deque
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