from fastapi import APIRouter
from model.course import CourseRequest, CreateReviewRequest, ReviewResponse
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

# 내가 만든 코스 조회
@router.get("/list")
def list_courses():
    data = course_data.list_courses()
    return {"success": True, "courses": data}

# 코스 조회 (리뷰 페아지로 이동)
@router.get("/{course_id}")
def get_course(course_id: int):
    course = course_data.get_course_by_id(course_id)
    return {"success": True, "course": course}

# 가장 최근 내가 적은 리뷰 띄우기
@router.get("/{course_id}/reviews/latest")
def get_latest_review(course_id: int):
    latest_review = course_data.get_latest_review(course_id)
    return {"success": True, "latestReview": latest_review}

# 리뷰 작성 + 업데이트
@router.post("/{course_id}")
def add_course_review(course_id: int, request: CreateReviewRequest = Body(...)):
    full_content = f"{request.title}\n{request.body}"
    new_reviews = course_data.review_courses(
        course_id=course_id,
        content=full_content,
        score=request.score,
        author_id=request.author_id
    )
    return {"success": True, "reviews": new_reviews}