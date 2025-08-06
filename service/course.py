from data.course import CourseData

class CourseService:
    def __init__(self):
        self.data = CourseData()

    def create_course(self, maker_id, name, content, rating):
        return self.data.create_course(maker_id, name, content, rating)

    def create_course_place(self, course_id, course_name, latitude, longitude):
        return self.data.create_course_place(course_id, course_name, latitude, longitude)