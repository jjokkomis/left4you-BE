from fastapi import APIRouter
from model.course import CourseRequest, CreateReviewRequest
from data.course import CourseData
from fastapi import Body, Query

router = APIRouter(prefix="/course")
course_data = CourseData()

@router.post("/create")
def create_course(request: CourseRequest):
    course_result, tour_item = course_data.create_course(
        maker_id=request.maker_id,
        name=request.name,
        content=request.content,
        rating=request.rating
    )
    course_id = course_result[0]["id"]
    place_result = course_data.create_course_place(
        course_id=course_id,
        place_name=request.place_name,
        latitude=request.latitude,
        longitude=request.longitude
    )
    return { "success": True, "course": course_result, "place": place_result, "tour_item": tour_item }

@router.get("/list")
def list_courses(user_id: int):
    data = course_data.list_courses(user_id)
    return {"success": True, "courses": data}

@router.get("/{course_id}")
def get_course(course_id: int):
    course = course_data.get_course_by_id(course_id)
    return {"success": True, "course": course}

@router.get("/{course_id}/reviews/latest")
def get_latest_review(course_id: int, user_id: int):
    latest_review = course_data.get_latest_review(course_id, user_id)
    return {"success": True, "latestReview": latest_review}

@router.post("/{course_id}")
def add_course_review(course_id: int, request: CreateReviewRequest = Body(...)):
    full_content = f"{request.title}\n{request.body}"
    new_reviews = course_data.review_courses(
        course_id=course_id,
        user_id=request.user_id,
        content=full_content,
        score=request.score
    )
    return {"success": True, "reviews": new_reviews}