from pydantic import BaseModel

class Course(BaseModel):
    maker_id: int
    name: str
    content: str
    rating: int

class CoursePlace(BaseModel):
    course_id: int
    place_name: str
    latitude: float
    longitude: float

class CourseRequest(BaseModel):
    maker_id: int
    name: str
    content: str
    rating: int
    place_name: str
    latitude: float
    longitude: float

class CreateReviewRequest(BaseModel):
    title: str
    body: str
    score: int
    user_id: int