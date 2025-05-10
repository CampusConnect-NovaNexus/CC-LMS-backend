from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime, timezone
# Create db instance without app
db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'courses'
    course_code = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String , nullable=False, unique=True)
    
    # Relationships
    exams = db.relationship('Exam', backref='course', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='course', cascade="all, delete-orphan")
    
    def json(self):
        return {
            'course_code': self.course_code,
            'course_name': self.course_name,
            'created_by': self.user_id
        }

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    roll_no = db.Column(db.String(10), primary_key=True)
    course_code = db.Column(db.String(20), db.ForeignKey('courses.course_code'))
    user_id = db.Column(db.String , nullable=False, unique=True)
    
    def json(self):
        return {
            'roll_no': self.roll_no,
            'course_code': self.course_code,
            'student_id': self.user_id
        }

class Exam(db.Model):
    __tablename__ = 'exams'
    exam_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    course_code = db.Column(db.String(20), db.ForeignKey('courses.course_code'))
    exam_type = db.Column(db.String(50), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.String , nullable=False, unique=True)
    pyq_pdf = db.Column(db.String(500), nullable=True)
    
    # Relationships
    syllabus_items = db.relationship('SyllabusItem', backref='exam', cascade="all, delete-orphan")
    
    def json(self):
        return {
            'exam_id': self.exam_id,
            'course_code': self.course_code,
            'exam_type': self.exam_type,
            'exam_date': self.exam_date.isoformat(),
            'created_by': self.user_id
        }

class SyllabusItem(db.Model):
    __tablename__ = 'syllabus_items'
    item_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = db.Column(db.String, db.ForeignKey('exams.exam_id'))
    parent_item_id = db.Column(db.String, db.ForeignKey('syllabus_items.item_id'), nullable=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.String , nullable=False, unique=True)
    
    # Relationships
    children = db.relationship('SyllabusItem', backref=db.backref('parent', remote_side=[item_id]))
    progress = db.relationship('ChecklistProgress', backref='item', cascade="all, delete-orphan")
    
    def json(self):
        return {
            'item_id': self.item_id,
            'exam_id': self.exam_id,
            'parent_item_id': self.parent_item_id,
            'description': self.description,
            'created_by': self.user_id
        }

class ChecklistProgress(db.Model):
    __tablename__ = 'checklist_progress'
    progress_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String , nullable=False, unique=True)
    item_id = db.Column(db.String, db.ForeignKey('syllabus_items.item_id'))
    is_completed = db.Column(db.Boolean, default=False)
    
    def json(self):
        return {
            'progress_id': self.progress_id,
            'student_id': self.user_id,
            'item_id': self.item_id,
            'is_completed': self.is_completed
        }

class Update(db.Model):
    __tablename__ = 'updates'
    update_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(512), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def json(self):
        return {
            'update_id': self.update_id,
            'title': self.title,
            'link': self.link,
            'sequence': self.sequence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }