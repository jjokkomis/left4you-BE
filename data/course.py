from supabase import create_client
import os
import requests

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

class CourseData:
    def create_course(self, maker_id: str, name: str, content: str, rating: int):
        TOUR_API_KEY = os.getenv("TOUR_API_KEY")
        url = "http://api.visitkorea.or.kr/openapi/service/rest/KorService/areaBasedList"

        params = {
            "ServiceKey": TOUR_API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "GiftTrip",
            "_type": "json",
            "areaCode": 8,
            "sigunguCode": 1,
            "contentTypeId": 12,
            "numOfRows": 1
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data_json = resp.json()
        tour_item = data_json.get("response", {}).get("body", {}).get("items", {}).get("item", {})
        response = supabase.table("course").insert({
            "maker_id": maker_id,
            "name": name,
            "content": content,
            "rating": rating,
        }).execute()
        return response.data, tour_item

    def create_course_place(self, course_id: int, place_name: str, latitude: float, longitude: float, seq: int = 1):
        response = supabase.table("course_place").insert({
            "course_id": course_id,
            "seq": seq,
            "place_name": place_name,
            "latitude": latitude,
            "longitude": longitude,
        }).execute()
        return response.data

    def list_courses(self):
        courses_resp = supabase.table("course").select("*").order("created_at", desc=True).limit(10).execute()
        courses = courses_resp.data or []

        places_resp = supabase.table("course_place").select("*").execute()
        places = places_resp.data or []

        for course in courses:
            course["places"] = [p for p in places if p["course_id"] == course["id"]]

        return courses

    # 만들기 페이지에서의 list 조회
    def get_course_by_id(self, course_id: int):
        resp = (
            supabase
            .table("course")
            .select("*")
            .eq("id", course_id)
            .execute())

        courses = resp.data or []
        course = courses[0]

        places_resp = (
            supabase
            .table("course_place")
            .select("*")
            .eq("course_id", course_id)
            .order("seq")
            .execute())

        course["places"] = places_resp.data or []

        return course

    def review_courses(self, course_id: int, author_id: int, content: str, score: int):
        result = supabase.table("review").upsert(
            {
                "course_id": course_id,
                "author_id": author_id,
                "content": content,
                "score": score
            },
            on_conflict="author_id"
        ).execute()

        return result.data

    def get_latest_review(self, course_id: int):
        response = (
            supabase
            .table("review")
            .select("*")
            .eq("course_id", course_id)
            .order("id", desc=True)
            .execute()
        )
        return response.data[0] if response.data else None