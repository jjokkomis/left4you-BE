from fastapi import APIRouter, Body
from fastapi.params import Depends

from service import survey as service
from utils import JWT

router = APIRouter(prefix="/survey")

@router.get('')
def get_survey(user_id: int = Depends(JWT.get_current_user_id)) :
    return service.get_survey(user_id)

@router.post('')
def save_survey(user_id: int = Depends(JWT.get_current_user_id), survey_result: dict = Body(...)) :
    return service.save_survey(user_id, survey_result)