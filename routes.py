from flask import Blueprint, request
from services import *

# Create a Blueprint
exam_bp = Blueprint('exam', __name__)

# Course routes
@exam_bp.route('/api/exam/courses', methods=['GET', 'POST'])
def handle_courses():
    if request.method == 'POST':
        return create_course_service()
    else:
        return get_courses_service()

# Get Courses a student is enrolled in
@exam_bp.route('/api/exam/students/<string:user_id>/courses', methods=['GET'])
def get_student_courses(user_id):
    return get_student_courses_service(user_id)

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
@exam_bp.route('/api/exam/students/<string:user_id>/enrollments', methods=['GET'])
def get_student_enrollments(user_id):
    return get_student_enrollments_service(user_id)

# Get all progress for a student
@exam_bp.route('/api/exam/students/<string:user_id>/progress', methods=['GET'])
def get_student_progress(user_id):
    return get_student_progress_service(user_id)

# Get upcoming exams for a student
@exam_bp.route('/api/exam/students/<string:user_id>/upcoming-exams', methods=['GET'])
def get_student_upcoming_exams(user_id):
    return get_student_upcoming_exams_service(user_id)

# Updates routes
@exam_bp.route('/api/notice/updates', methods=['POST'])
def fetch_updates():
    return get_updates_service()

@exam_bp.route('/api/notice/stored-updates', methods=['GET'])
def get_stored_updates():
    return get_stored_updates_service()

@exam_bp.route('/api/pyq/add', methods=['POST'])
def add_pyq():
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = {
            'exam_id': request.form.get('exam_id'),
            'pdf_file': request.files.get('pdf_file') if 'pdf_file' in request.files else None
        }

        print("Data from form:", data)
    else:
        data = request.get_json()
    return add_pyq_service(data)

@exam_bp.route('/api/pyq/<string:exam_id>', methods=['GET'])
def get_pyq(exam_id):
    return get_pyq_service(exam_id)
    