from data.course import CourseData


class CourseService:
    def __init__(self):
        self.data = CourseData()

    def create_course(self, maker_id, name, content, rating):
        return self.data.create_course(maker_id, name, content, rating)

    def create_course_place(self, course_id, place_name, latitude, longitude, seq=1):
        return self.data.create_course_place(course_id, place_name, latitude, longitude, seq)

    def add_review(self, course_id: int, author_id: int, content: str, score: int):
        return self.data.review_courses(course_id, author_id, content, score)