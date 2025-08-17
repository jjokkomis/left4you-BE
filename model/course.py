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

class CreateCourseRequest(BaseModel):
    course: Course
    place: CoursePlace

class UpdateCourseRequest(BaseModel):
    course_id: int
    title: str
    body: str
    rating: int

class CourseRequest(BaseModel):
    maker_id: int
    name: str
    content: str
    rating: int
    place_name: str
    latitude: float
    longitude: float