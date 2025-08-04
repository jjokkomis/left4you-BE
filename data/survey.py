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