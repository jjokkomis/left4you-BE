from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

class CourseData:
    def create_course(self, maker_id: str, name: str, content: str, rating: int):
        response = (
            supabase
            .table("course")
            .insert({
                "maker_id": maker_id,
                "name": name,
                "content": content,
                "rating": rating,
            })
            .execute()
        )
        return response.data

    def create_course_place(self, course_id: int, place_name: str, latitude: float, longitude: float):
        response = (
            supabase
            .table("course_place")
            .insert({
                "course_id": course_id,
                "seq": 1,
                "place_name": place_name,
                "latitude": latitude,
                "longitude": longitude,
            })
            .execute()
        )
        return response.data


def list_courses():
    response = (
        supabase
        .table("course_with_place")
        .select("*")
        .order("course_id", desc=True)
        .limit(1)
        .execute()
    )
    return response.data
