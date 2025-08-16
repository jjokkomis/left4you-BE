# web/receive.py
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from typing import Optional
from service import receive as service
from utils import JWT  # 기존 인증 그대로

router = APIRouter(prefix="/receive", tags=["receive"])

@router.get("/recommend/{city}")
def recommend_giftdata(user_id: int = Depends(JWT.get_current_user_id), city: Optional[str] = None):
    try:
        result = service.recommend_giftdata(user_id=user_id, city=city, region=city)
    except HTTPException as e:
        raise e
    if result is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return result
