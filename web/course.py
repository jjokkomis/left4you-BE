from fastapi import APIRouter, Body
from model.course import CourseCreateRequest
from service import course as service
from data.course import list_courses as db

router = APIRouter(prefix="/course")

@router.post("/create")
def create_course(request: CourseCreateRequest):
    coordA = request.content.coordA
    coordB = request.content.coordB

    result = service.create_course(
        request.maker_id,
        request.name,
        coordA,
        coordB,
        request.rating,
        request.message
    )

    if result.get("success"):
        return {
            "success": True,
            "courseId": result["course_id"]
        }
    else:
        return {
            "success": False,
            "message": result.get("message", "Unknown error")
        }


@router.get("/list")
def list_courses():
    data = db()
    return data