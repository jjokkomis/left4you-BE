from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

def create_course(maker_id, name, coordA, coordB, rating, message):
    response = supabase.table("course").insert({
        "maker_id": maker_id,
        "name": name,
        "content": {
            "coordA": coordA.dict(),
            "coordB": coordB.dict()
        },
        "rating": rating,
        "message": message
    }).execute()

    if response.data:
        return {"success": True, "course_id": response.data[0]["id"]}
    else:
        return {"success": False, "message": "데이터 삽입 실패"}

def list_courses():
    response = (
        supabase
        .table("course")
        .select("name, content, maker_id")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    if response.data:
        return {"success": True, "courses": response.data}
    else:
        return {"success": True, "courses": []}
