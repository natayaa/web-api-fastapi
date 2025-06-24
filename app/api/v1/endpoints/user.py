from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse

user_endpoint = APIRouter(tags=["User Information"])

#
#@user_endpoint.post("/")