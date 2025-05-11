from flask import request, jsonify, make_response
from models import db, Course, Exam, SyllabusItem, Enrollment, Update
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
from file_upload_service import file_upload

# Course service functions
def create_course_service():
    try:
        data = request.get_json()
        new_course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            user_id=data['user_id']
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
            user_id=data['user_id']
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
            description=data['description'],
            user_id=data['user_id']
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
        user_id = data.get('user_id')
        
        # Check if enrollment already exists
        existing = Enrollment.query.filter_by(
            course_code=course_code,
            user_id=user_id
        ).first()
        
        if existing:
            return jsonify({"message": "Student already enrolled"}), 200
        
        enrollment = Enrollment(
            course_code=course_code,
            user_id=user_id,
        )
        db.session.add(enrollment)
        db.session.commit()
        return jsonify({"message": "Enrolled successfully"}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error enrolling student", 'error': str(e)}), 500)

# Progress service functions
# def update_progress_service(item_id):
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')
        
#         progress = ChecklistProgress.query.filter_by(
#             user_id=user_id,
#             item_id=item_id
#         ).first()
        
#         if not progress:
#             progress = ChecklistProgress(
#                 user_id=user_id,
#                 item_id=item_id,
#                 is_completed=data.get('completed', True)
#             )
#             db.session.add(progress)
#         else:
#             progress.is_completed = not progress.is_completed
        
#         db.session.commit()
#         return jsonify({"completed": progress.is_completed}), 200
#     except Exception as e:
#         return make_response(jsonify({'message': "Error updating progress", 'error': str(e)}), 500)

def get_student_enrollments_service(user_id):
    try:
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        courses = []
        
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_code)
            if course:
                courses.append(course.json())
        
        return jsonify(courses), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting enrollments", 'error': str(e)}), 500)


def update_progress_service(item_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        done = data.get('done')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
            
        progress = SyllabusItem.query.filter_by(item_id=item_id).first()
        
        if not progress:
            if done:
                progress = SyllabusItem(
                    item_id=item_id,
                    completers=[user_id]
                )
                db.session.add(progress)
            else:
                return jsonify({"message": "Item not found", "len_completers": 0}), 200
        else:
            if progress.completers is None:
                progress.completers = []
            
            user_in_completers = False
            if progress.completers:
                for completer in progress.completers:
                    if completer == user_id:
                        user_in_completers = True
                        break
            
            
            if done:
                if not user_in_completers:
                    progress.completers.append(user_id)
                else:
                    print(f"User {user_id} already in completers, no change needed")
            else:
                if user_in_completers:
                    progress.completers.remove(user_id)
                else:
                    print(f"User {user_id} not in completers, no change needed")
        
        if not isinstance(progress.completers, list):
            progress.completers = list(progress.completers) if progress.completers else []
        
        progress.completers = list(set(progress.completers))
        
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(progress, 'completers')
        
        completersLength = len(progress.completers)
        
        db.session.commit()
        
        exam = Exam.query.filter_by(exam_id=progress.exam_id).first()
        total_students = 0
        
        if exam:
            course = Course.query.filter_by(course_code=exam.course_code).first()
            if course:
                enrollments = Enrollment.query.filter_by(course_code=course.course_code).all()
                total_students = len(enrollments)
            else:
                print("Course not found")
        else:
            print("Exam not found")
        
        response_data = {
            "len_completers": completersLength,
            "action": "added" if done else "removed",
            "stats": {
                "total_students": total_students,
                "who_studied": completersLength,
                "completers": progress.completers
            }
        }
        
        
        return jsonify(response_data), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'message': "Error updating progress", 'error': str(e)}), 500

def get_student_progress_service(user_id):
    try:
        progress_items = SyllabusItem.query.filter_by().all()
        return jsonify([item.json() for item in progress_items]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting progress", 'error': str(e)}), 500)

def get_syllabus_item_stats_service(item_id):
    try:
        # Get the syllabus item
        syllabus_item = SyllabusItem.query.filter_by(item_id=item_id).first()
        
        if not syllabus_item:
            return jsonify({"error": "Syllabus item not found"}), 404
        
        # Get the exam associated with this syllabus item
        exam = Exam.query.filter_by(exam_id=syllabus_item.exam_id).first()
        
        if not exam:
            return jsonify({"error": "Exam not found for this syllabus item"}), 404
        
        # Get the course associated with this exam
        course = Course.query.filter_by(course_code=exam.course_code).first()
        
        if not course:
            return jsonify({"error": "Course not found for this exam"}), 404
        
        # Get all enrollments for this course to determine total students
        enrollments = Enrollment.query.filter_by(course_code=course.course_code).all()
        total_students = len(enrollments)
        
        # Get the number of students who have completed this item
        completers = syllabus_item.completers or []
        who_studied = len(completers)
        
        return jsonify({
            "stats": {
                "total_students": total_students,
                "who_studied": who_studied,
                "completers": completers
            },
            "item_id": item_id,
            "description": syllabus_item.description
        }), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting syllabus item stats", 'error': str(e)}), 500)

# Get progress of every syllabus item
def get_progress_syllabus_items_service(item_id):
    try:
        progress_items = SyllabusItem.query.filter_by(item_id=item_id).first()
        if progress_items:
            return jsonify({SyllabusItem.json(progress_items)}), 200
        else:
            return make_response(jsonify({'message': "Item not found"}), 404)
    except Exception as e:
        return make_response(jsonify({'message': "Error getting progress", 'error': str(e)}), 500)
    
# Get Courses a student is enrolled in
def get_student_courses_service(user_id):
    try:
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        courses = []
        
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_code)
            if course:
                courses.append(course.json())
        
        return jsonify(courses), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting enrollments", 'error': str(e)}), 500)

# Get upcoming exams for a student
def get_student_upcoming_exams_service(user_id):
    try:
        # Get current date and time
        current_datetime = datetime.now()
        
        # Get all courses the student is enrolled in
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        course_codes = [enrollment.course_code for enrollment in enrollments]
        
        # Query for exams in those courses that have a date in the future
        upcoming_exams = Exam.query.filter(
            Exam.course_code.in_(course_codes),
            Exam.exam_date > current_datetime
        ).order_by(Exam.exam_date).all()
        
        # Format the response
        result = []
        for exam in upcoming_exams:
            course = Course.query.get(exam.course_code)
            exam_data = exam.json()
            exam_data['course_name'] = course.course_name if course else "Unknown Course"
            result.append(exam_data)
            
        return jsonify(result), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error getting upcoming exams", 'error': str(e)}), 500)

# Updates service functions
def get_updates_service():
    try:
        url = request.json.get('url')
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        target_div = soup.find('div', class_='studentDownloadBox accordion')
        
        if target_div:
            items = target_div.find_all('li')[:10]
            notifications = []
            
            # Clear existing updates to maintain the same sequence
            Update.query.delete()
            
            # Add new updates with sequence numbers
            for idx, item in enumerate(items):
                a_tag = item.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = a_tag.get("href")
                    full_link = "https://www.nitm.ac.in/" + link
                    
                    # Create a new update record with sequence
                    new_update = Update(
                        title=title,
                        link=full_link,
                        sequence=idx  # Use index as sequence (0-based)
                    )
                    db.session.add(new_update)
                    
                    notifications.append({
                        "update_id": new_update.update_id,
                        "title": title,
                        "link": full_link,
                        "sequence": idx,
                        "created_at": new_update.created_at.isoformat() if new_update.created_at else None
                    })
            
            # Commit all new updates to the database
            db.session.commit()
            
            return jsonify(notifications), 200
        else:
            return make_response(jsonify({'message': "Section not found"}), 404)
    except Exception as e:
        return make_response(jsonify({'message': "Error fetching updates", 'error': str(e)}), 500)

def get_stored_updates_service():
    try:
        # Get all updates from the database, ordered by sequence (to maintain original order)
        updates = Update.query.order_by(Update.sequence).all()
        return jsonify([update.json() for update in updates]), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error retrieving updates", 'error': str(e)}), 500)

def add_pyq_service(data):
    try:
        exam_id = data['exam_id']
        pdf_file = data['pdf_file']
        if not pdf_file:
            return make_response(jsonify({'message': "No PDF file provided"}), 400)

        exam = Exam.query.get(exam_id)
        if not exam:
            return make_response(jsonify({'message': "Exam not found"}), 404)

        try: 
            if pdf_file:
                filename = f"{exam_id}_{pdf_file.filename}"
                upload_response = file_upload(pdf_file, filename)
                if upload_response:
                    # Extract the URL from the ImageKit response
                    pdf_file_url = upload_response.get('url')
        except Exception as e:
            return make_response(jsonify({'message': "Error uploading file", 'error': str(e)}), 500)

        exam.pyq_pdf = pdf_file_url; 
        db.session.commit()

        return jsonify({"message": "PYQ added successfully"}), 201
    except Exception as e:
        return make_response(jsonify({'message': "Error adding PYQ", 'error': str(e)}), 500)

def get_pyq_service(exam_id):
    try:
        exam = Exam.query.get(exam_id)
        if not exam:
            return make_response(jsonify({'message': "Exam not found"}), 404)

        return jsonify({"pyq_pdf": exam.pyq_pdf}), 200
    except Exception as e:
        return make_response(jsonify({'message': "Error retrieving PYQ", 'error': str(e)}), 500)