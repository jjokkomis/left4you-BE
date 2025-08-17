from fastapi import APIRouter
from model.course import UpdateCourseRequest, CourseRequest
from data.course import CourseData

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

# 최신 코스 1개 조회
@router.get("/list")
def get_latest_course():
    data = course_data.list_review_courses(limit=1)
    return {"success": True, "courses": data}

# 리뷰 코스 조회
@router.get("/review")
def get_review_courses():
    data = course_data.list_review_courses(limit=20)
    return {"success": True, "courses": data}

# 코스 리뷰 수정
@router.put("/update")
def update_course(request: UpdateCourseRequest):
    full_content = f"{request.title}\n{request.body}"

    updated_course = course_data.update_course(
        course_id=request.course_id,
        content=full_content,
        rating=request.rating
    )

    return {"success": True, "course": updated_course}

# 코스 단일 조회
@router.get("/{course_id}")
def get_course(course_id: int):
    course = course_data.get_course_by_id(course_id)

    return {"success": True, "course": course}

# 선물 받은 코스 조회
@router.get("/gift/{course_id}")
def list_course_gift(course_id: int):
    course = course_data.list_gift_course(course_id)
    return {"success": True, "courses": course}
