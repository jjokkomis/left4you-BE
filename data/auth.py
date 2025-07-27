from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def get_user_by_kakao_id(kakao_id: int):
    resp = (
        supabase
        .table("user")
        .select("*")
        .eq("kakao_id", kakao_id)
        .limit(1)             # single() 대신 limit(1)
        .execute()
    )
    data = resp.data        # 리스트 또는 []
    return data[0] if data else None

def create_user(kakao_id: int, name: str, profile: str):
    resp = (
        supabase
        .table("user")
        .insert({ "kakao_id": kakao_id, "name": name, "profile": profile })
        .execute()            # insert 후에도 .limit 필요 없음
    )
    data = resp.data        # [{...}] 형태
    return data[0] if data else None
