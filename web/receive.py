from fastapi import APIRouter, Body, Depends, HTTPException, Response, status, Query, Path
from typing import Optional
from service import receive as service
from utils import JWT  # 기존 인증

router = APIRouter(prefix="/receive", tags=["receive"])

@router.get("/recommend/{city}")
def recommend_giftdata(
    city: str = Path(..., description="영문 CITY 코드 (예: SEOUL, GYEONGGI)"),
    # 프론트 호환: camelCase/snake_case 모두 허용
    exclude_course_id: Optional[int] = Query(None, alias="exclude_course_id", description="이 코스 제외하고 재추천"),
    excludeCourseId: Optional[int] = Query(None, alias="excludeCourseId"),
    user_id: int = Depends(JWT.get_current_user_id),
):
    city = (city or "").upper()
    ecid = exclude_course_id or excludeCourseId

    try:
        result = service.recommend_giftdata(
            user_id=user_id,
            city=city,
            exclude_course_id=ecid,
        )
    except HTTPException as e:
        raise e

    if result is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return result

@router.post("/claim")
def claim(
    payload: dict = Body(...),
    user_id: int = Depends(JWT.get_current_user_id)
):
    city = (payload.get("city") or payload.get("region") or "").upper()
    course_id = payload.get("course_id")

    if not city:
        raise HTTPException(status_code=400, detail="city_required")

    return service.claim_course(
        user_id=user_id,
        city=city,
        course_id=course_id
    )

@router.get("/gifts")
def list_my_gifts(user_id: int = Depends(JWT.get_current_user_id)):
    """
    GET /receive/gifts
    응답: [
      {
        "gift_id": 12031,
        "course_id": 1850,
        "claimed_at": "2025-08-17T09:21:00.123456+00:00",
        "course_name": "한강 야경 산책",
        "rating_avg": 4.3,
        "rating_count": 12
      },
      ...
    ]
    """
    return service.list_all_my_gifts(user_id=user_id)