import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from service import auth

router = APIRouter()

@router.get("/auth/kakao/login")
def kakao_login():
    kakao_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={os.getenv('KAKAO_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('KAKAO_REDIRECT_URI')}"
        "&response_type=code"
        "&scope=profile_nickname,profile_image"
    )
    return RedirectResponse(kakao_url)

@router.get("/auth/kakao/callback")
async def kakao_callback(code: str = Query(...)):
    try:
        token = await auth.login_or_signup_kakao(code)
    except Exception as e:
        raise HTTPException(400, f"Kakao OAuth failed: {e}")
    return token
