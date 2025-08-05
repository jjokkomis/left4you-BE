from postgrest import APIError
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_survey(user_id: int) :
    resp = (
        supabase
        .table("survey")
        .select("*", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    print(resp)
    return resp


def save_survey(user_id, survey_result: dict) :
    records = [
        {
            "user_id": user_id,
            "type": k.upper(),
            "value": v,
        }
        for k, v in survey_result.items()
    ]

    try:
        supabase.table("survey").insert(records).execute()
    except APIError as e:
        raise Exception(f"설문 저장 실패: {e.message}")

    return None