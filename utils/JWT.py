from datetime import timedelta, datetime, timezone

import jwt
import os

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import ExpiredSignatureError, InvalidTokenError

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES=60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/kakao/token",
    scheme_name="JWT"
)

def create_access_token(payload: dict, expires_delta: timedelta = timedelta(minutes=60)):
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode.update({"iat": now, "exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["user_id"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="잘못된 토큰입니다.")