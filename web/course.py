from fastapi import APIRouter
from data.course import list_courses as db
from model.course import CreateCourseRequest
from data.course import CourseData;

router = APIRouter(prefix="/course")

@router.post("/create")
def create_course_endpoint(request: CreateCourseRequest):
    course = request.course
    place = request.place

    course_data = CourseData()

    course_result = course_data.create_course(
        maker_id=course.maker_id,
        name=course.name,
        content=course.content,
        rating=course.rating
    )

    course_place_result = course_data.create_course_place(
        course_id=course_result[0]["id"],
        place_name=place.place_name,
        latitude=place.latitude,
        longitude=place.longitude
    )

@router.get("/list")
def list_courses():
    data = db()
    return {"success": True, "courses": data}