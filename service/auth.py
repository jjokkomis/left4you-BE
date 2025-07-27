import os, httpx, jwt
from data import auth as data

KAKAO_CLIENT_ID     = os.getenv("KAKAO_CLIENT_ID")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
KAKAO_REDIRECT_URI  = os.getenv("KAKAO_REDIRECT_URI")
JWT_SECRET          = os.getenv("JWT_SECRET")
JWT_ALGORITHM       = os.getenv("JWT_ALGORITHM", "HS256")

async def exchange_kakao_token(code: str) -> dict:
    data = {
        "grant_type":   "authorization_code",
        "client_id":    KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code":         code,
    }
    if KAKAO_CLIENT_SECRET:
        data["client_secret"] = KAKAO_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data=data,
            headers={"Content-Type":"application/x-www-form-urlencoded"}
        )
        r.raise_for_status()
        return r.json()

async def fetch_kakao_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        r.raise_for_status()
        return r.json()

async def login_or_signup_kakao(code: str) -> dict:
    # 1) 인가 코드 → 카카오 access_token
    tokens  = await exchange_kakao_token(code)
    # 2) access_token → 프로필
    profile = await fetch_kakao_profile(tokens["access_token"])

    kakao_id    = profile["id"]
    kakao_acc   = profile.get("kakao_account", {}).get("profile", {}) \
                  or profile.get("properties", {})
    nickname    = kakao_acc.get("nickname", "")
    profile_img = kakao_acc.get("profile_image_url", "")

    # 3) Supabase에서 조회/생성 (dict or None 반환)
    user = data.get_user_by_kakao_id(kakao_id)
    if user is None:
        user = data.create_user(kakao_id, nickname, profile_img)

    # 4) JWT 발급 (payload에 user_id만 담음)
    payload   = { "user_id": user["id"] }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # 5) 토큰과 유저 정보를 함께 반환
    return {
        "access_token": jwt_token,
        "token_type":   "bearer",
        "user": {
            "id":      user["id"],
            "name":    user["name"],
            "profile": user["profile"],
        }
    }