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

    def list_review_courses(self, limit: int = 20):
        response = (
            supabase
            .table("course")
            .select("*")
            .order("id", desc=True)
            .range(0, limit - 1)
            .execute())

        courses = response.data or []

        for course in courses:
            response = (
                supabase
                .table("course_place")
                .select("*")
                .eq("course_id", course["id"])
                .order("seq")
                .execute())
            course["places"] = response.data or []

        return courses

    def update_course(self, course_id: int, content: str, rating: int):
        response = (
            supabase
            .table("course")
            .update({"content": content, "rating": rating})
            .eq("id", course_id)
            .execute()
        )

        updated_course = response.data[0] if response.data else None

        return updated_course

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

    def list_gift_course(self, course_id: int):
        resp = (
            supabase
            .table("course_gift")
            .select("*")
            .eq("course_id", course_id)
            .execute()
        )

        return resp.data