from pydantic import BaseModel

class Coordinates(BaseModel):
    lat: float
    lng: float

class Content(BaseModel):
    coordA: Coordinates
    coordB: Coordinates

class CourseCreateRequest(BaseModel):
    maker_id: str
    name: str
    content: Content
    rating: int
    message: str