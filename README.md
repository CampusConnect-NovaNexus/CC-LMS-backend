# Campus Connect LMS API Documentation

## API Overview
This documentation provides details on the Campus Connect Exam API endpoints, their usage, and the database structure to help frontend developers integrate with the backend.

## Database Structure

### Entity Relationship Diagram
```
┌─────────┐       ┌───────────┐     ┌───────────┐
│  User   │       │ Course    │     │   Exam    │
├─────────┤       ├───────────┤     ├───────────┤
│ user_id │◄──┐   │course_code│◄─┐  │ exam_id   │
│ username│   │   │course_name│  │  │course_code│
│ email   │   │   │created_by │──┘  │exam_type  │
└─────────┘   │   └───────────┘     │exam_date  │
     ▲        │        ▲            │created_by │
     │        │        │            └───────────┘
     │        │        │                  ▲
┌────┴──────┐ │   ┌────┴──────┐           │
│Syllabus   │ │   │Enrollment │      ┌────┴──────┐
│  Item     │ │   ├───────────┤      │Checklist  │
├───────────┤ │   │ roll_no   │      │Progress   │
│ item_id   │ │   │course_code│      ├───────────┤
│ exam_id   │ │   │student_id │──┐   │progress_id│
│parent_id  │ └───┤           │  │   │student_id │
│description│     └───────────┘  └───┤ item_id   │
│created_by │                        │completed  │
└───────────┘                        └───────────┘
```

### Tables Description

1. **User**
   - Primary key: `user_id`
   - Stores user information including username and email
   - Relationships: Creates courses, exams, and syllabus items

2. **Course**
   - Primary key: `course_code`
   - Stores course information
   - Foreign key: `created_by` references `User.user_id`
   - Relationships: Has exams and enrollments

3. **Enrollment**
   - Primary key: `roll_no`
   - Links students to courses
   - Foreign keys: `course_code`, `student_id`

4. **Exam**
   - Primary key: `exam_id`
   - Stores exam information
   - Foreign keys: `course_code`, `created_by`
   - Relationships: Has syllabus items

5. **SyllabusItem**
   - Primary key: `item_id`
   - Stores syllabus information in a hierarchical structure
   - Foreign keys: `exam_id`, `parent_item_id`, `created_by`
   - Relationships: Has child items and progress tracking

6. **ChecklistProgress**
   - Primary key: `progress_id`
   - Tracks student progress on syllabus items
   - Foreign keys: `student_id`, `item_id`

## API Endpoints

### User Management

#### Create User
- **Endpoint**: `POST /api/exam/users`
- **Description**: Creates a new user
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User created successfully",
    "user": {
      "user_id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
  }
  ```
- **Status Codes**:
  - 201: User created successfully
  - 500: Error creating user

### Course Management

#### Create Course
- **Endpoint**: `POST /api/exam/courses`
- **Description**: Creates a new course
- **Request Body**:
  ```json
  {
    "course_code": "CS101",
    "course_name": "Introduction to Computer Science",
    "description": "Basic computer science concepts",
    "user_id": 1
  }
  ```
- **Response**:
  ```json
  {
    "message": "Course created successfully"
  }
  ```
- **Status Codes**:
  - 201: Course created successfully
  - 500: Error creating course

#### Get All Courses
- **Endpoint**: `GET /api/exam/courses`
- **Description**: Retrieves all courses
- **Response**:
  ```json
  [
    {
      "course_code": "CS101",
      "course_name": "Introduction to Computer Science",
      "created_by": 1
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error getting courses

### Exam Management

#### Create Exam
- **Endpoint**: `POST /api/exam/courses/{course_code}/exams`
- **Description**: Creates a new exam for a specific course
- **URL Parameters**:
  - `course_code`: Course code
- **Request Body**:
  ```json
  {
    "exam_type": "Midterm",
    "exam_date": "2023-12-15T09:00:00",
    "user_id": 1
  }
  ```
- **Response**:
  ```json
  {
    "message": "Exam created successfully",
    "exam_id": 1
  }
  ```
- **Status Codes**:
  - 201: Exam created successfully
  - 500: Error creating exam

#### Get Course Exams
- **Endpoint**: `GET /api/exam/courses/{course_code}/exams`
- **Description**: Retrieves all exams for a specific course
- **URL Parameters**:
  - `course_code`: Course code
- **Response**:
  ```json
  [
    {
      "exam_id": 1,
      "course_code": "CS101",
      "exam_type": "Midterm",
      "exam_date": "2023-12-15T09:00:00",
      "created_by": 1
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error getting exams

### Syllabus Management

#### Add Syllabus Item
- **Endpoint**: `POST /api/exam/exams/{exam_id}/syllabus`
- **Description**: Adds a syllabus item to an exam
- **URL Parameters**:
  - `exam_id`: Exam ID
- **Request Body**:
  ```json
  {
    "description": "Data Structures",
    "parent_item_id": null,
    "user_id": 1
  }
  ```
- **Response**:
  ```json
  {
    "message": "Syllabus item added successfully",
    "item_id": 1
  }
  ```
- **Status Codes**:
  - 201: Syllabus item added successfully
  - 500: Error adding syllabus item

#### Get Syllabus Items
- **Endpoint**: `GET /api/exam/exams/{exam_id}/syllabus`
- **Description**: Retrieves all syllabus items for an exam
- **URL Parameters**:
  - `exam_id`: Exam ID
- **Response**:
  ```json
  [
    {
      "item_id": 1,
      "exam_id": 1,
      "parent_item_id": null,
      "description": "Data Structures",
      "created_by": 1
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error getting syllabus items

### Enrollment Management

#### Enroll Student
- **Endpoint**: `POST /api/exam/courses/{course_code}/enroll`
- **Description**: Enrolls a student in a course
- **URL Parameters**:
  - `course_code`: Course code
- **Request Body**:
  ```json
  {
    "student_id": 2,
    "roll_no": "CS2023001"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Enrolled successfully"
  }
  ```
- **Status Codes**:
  - 201: Enrolled successfully
  - 200: Student already enrolled
  - 500: Error enrolling student

#### Get Student Enrollments
- **Endpoint**: `GET /api/exam/students/{student_id}/enrollments`
- **Description**: Retrieves all courses a student is enrolled in
- **URL Parameters**:
  - `student_id`: Student ID
- **Response**:
  ```json
  [
    {
      "course_code": "CS101",
      "course_name": "Introduction to Computer Science",
      "created_by": 1
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error getting enrollments

### Progress Tracking

#### Update Progress
- **Endpoint**: `PUT /api/exam/checklist/{item_id}`
- **Description**: Updates a student's progress on a syllabus item
- **URL Parameters**:
  - `item_id`: Syllabus item ID
- **Request Body**:
  ```json
  {
    "student_id": 2,
    "completed": true
  }
  ```
- **Response**:
  ```json
  {
    "completed": true
  }
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error updating progress

#### Get Student Progress
- **Endpoint**: `GET /api/exam/students/{student_id}/progress`
- **Description**: Retrieves a student's progress on all syllabus items
- **URL Parameters**:
  - `student_id`: Student ID
- **Response**:
  ```json
  [
    {
      "progress_id": 1,
      "student_id": 2,
      "item_id": 1,
      "is_completed": true
    }
  ]
  ```
- **Status Codes**:
  - 200: Success
  - 500: Error getting progress
