from flask import request, jsonify, make_response
from models import db, User, Course, Exam, SyllabusItem, Enrollment, ChecklistProgress

# User service functions
def create_user_service():
    try:
        data = request.get_json()
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "user": new_user.json()}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error creating user", 'error': str(e)}), 500)

# Course service functions
def create_course_service():
    try:
        data = request.get_json()
        new_course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            created_by=data['user_id']
        )
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Course created successfully"}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error creating course", 'error': str(e)}), 500)

def get_courses_service():
    try:
        courses = db.session.query(Course).all()
        return jsonify([course.json() for course in courses]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting courses", 'error': str(e)}), 500)

# Exam service functions
def create_exam_service(course_code):
    try:
        data = request.get_json()
        new_exam = Exam(
            course_code=course_code,
            exam_type=data['exam_type'],
            exam_date=data['exam_date'],
            created_by=data['user_id']
        )
        db.session.add(new_exam)
        db.session.commit()
        return jsonify({"message": "Exam created successfully", "exam_id": new_exam.exam_id}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error creating exam", 'error': str(e)}), 500)

def get_exams_service(course_code):
    try:
        exams = Exam.query.filter_by(course_code=course_code).all()
        return jsonify([exam.json() for exam in exams]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting exams", 'error': str(e)}), 500)

# Syllabus service functions
def add_syllabus_item_service(exam_id):
    try:
        data = request.get_json()
        new_item = SyllabusItem(
            exam_id=exam_id,
            parent_item_id=data.get('parent_item_id'),
            description=data['description'],
            created_by=data['user_id']
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Syllabus item added successfully", "item_id": new_item.item_id}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error adding syllabus item", 'error': str(e)}), 500)

def get_syllabus_items_service(exam_id):
    try:
        items = SyllabusItem.query.filter_by(exam_id=exam_id).all()
        return jsonify([item.json() for item in items]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting syllabus items", 'error': str(e)}), 500)

# Enrollment service functions
def enroll_student_service(course_code):
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        roll_no = data.get('roll_no')
        
        # Check if enrollment already exists
        existing = Enrollment.query.filter_by(
            course_code=course_code,
            student_id=student_id
        ).first()
        
        if existing:
            return jsonify({"message": "Student already enrolled"}), 200
        
        enrollment = Enrollment(
            course_code=course_code,
            student_id=student_id,
            roll_no=roll_no
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "Enrolled successfully"}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error enrolling student", 'error': str(e)}), 500)

# Progress service functions
def update_progress_service(item_id):
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        
        progress = ChecklistProgress.query.filter_by(
            student_id=student_id,
            item_id=item_id
        ).first()
        
        if not progress:
            progress = ChecklistProgress(
                student_id=student_id,
                item_id=item_id,
                is_completed=data.get('completed', True)
            )
            db.session.add(progress)
        else:
            progress.is_completed = not progress.is_completed
        
        db.session.commit()
        return jsonify({"completed": progress.is_completed}), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error updating progress", 'error': str(e)}), 500)

def get_student_enrollments_service(student_id):
    try:
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        courses = []
        
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_code)
            if course:
                courses.append(course.json())
        
        return jsonify(courses), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting enrollments", 'error': str(e)}), 500)

def get_student_progress_service(student_id):
    try:
        progress_items = ChecklistProgress.query.filter_by(student_id=student_id).all()
        return jsonify([item.json() for item in progress_items]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting progress", 'error': str(e)}), 500)