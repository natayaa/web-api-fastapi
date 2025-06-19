from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

auth_route = APIRouter(tags=['Authentication'])

@auth_route.post("/login")
async def login():
    pass

@auth_route.post("/refresh-token")
async def refresh_token():
    pass