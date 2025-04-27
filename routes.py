from flask import Blueprint, request
from services import *

# Create a Blueprint
exam_bp = Blueprint('exam', __name__)

# User route
@exam_bp.route('/api/exam/users', methods=['POST'])
def create_user():
    return create_user_service()

# Course routes
@exam_bp.route('/api/exam/courses', methods=['GET', 'POST'])
def handle_courses():
    if request.method == 'POST':
        return create_course_service()
    else:
        return get_courses_service()

# Exam routes
@exam_bp.route('/api/exam/courses/<course_code>/exams', methods=['GET', 'POST'])
def handle_exams(course_code):
    if request.method == 'POST':
        return create_exam_service(course_code)
    else:
        return get_exams_service(course_code)

# Syllabus routes
@exam_bp.route('/api/exam/exams/<string:exam_id>/syllabus', methods=['GET', 'POST'])
def handle_syllabus(exam_id):
    if request.method == 'POST':
        return add_syllabus_item_service(exam_id)
    else:
        return get_syllabus_items_service(exam_id)

# Enrollment routes relate the student to the course
@exam_bp.route('/api/exam/courses/<course_code>/enroll', methods=['POST'])
def enroll_student(course_code):
    return enroll_student_service(course_code)

# Progress routes
@exam_bp.route('/api/exam/checklist/<int:item_id>', methods=['PUT'])
def update_progress(item_id):
    return update_progress_service(item_id)

# Get all enrollments for a student
@exam_bp.route('/api/exam/students/<string:student_id>/enrollments', methods=['GET'])
def get_student_enrollments(student_id):
    return get_student_enrollments_service(student_id)

# Get all progress for a student
@exam_bp.route('/api/exam/students/<string:student_id>/progress', methods=['GET'])
def get_student_progress(student_id):
    return get_student_progress_service(student_id)