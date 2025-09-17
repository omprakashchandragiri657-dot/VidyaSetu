# Smart Student Hub API Endpoints

This document provides a comprehensive list of all API endpoints available in the Smart Student Hub application. All endpoints are prefixed with `/api/` and require appropriate authentication.

## Authentication

### JWT Token Endpoints
- **POST** `/api/token/`
  - **Description**: Obtain JWT access and refresh tokens
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
  - **Response**: JWT tokens

- **POST** `/api/token/refresh/`
  - **Description**: Refresh JWT access token
  - **Request Body**:
    ```json
    {
      "refresh": "string"
    }
    ```
  - **Response**: New access token

### Login Endpoints
- **POST** `/api/user-login/`
  - **Description**: User login for students, faculty, HOD, principal
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
  - **Response**: User details and role information

- **POST** `/api/admin-login/`
  - **Description**: Admin login for superusers
  - **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
  - **Response**: Admin user details

## Superuser Endpoints

### College Management
- **GET** `/api/colleges/`
  - **Description**: List all colleges
  - **Permissions**: Superuser
  - **Response**: List of colleges with details

- **POST** `/api/colleges/create/`
  - **Description**: Create a new college
  - **Permissions**: Superuser
  - **Request Body**:
    ```json
    {
      "name": "string",
      "code": "string",
      "address": "string",
      "contact_email": "string",
      "contact_phone": "string"
    }
    ```

- **GET** `/api/colleges/<id>/`
  - **Description**: Get college details
  - **Permissions**: Superuser or college management permission
  - **Response**: College details with principal information

- **PUT/PATCH** `/api/colleges/<id>/`
  - **Description**: Update college details
  - **Permissions**: Superuser or college management permission

- **DELETE** `/api/colleges/<id>/`
  - **Description**: Delete college
  - **Permissions**: Superuser

### Department Management
- **GET** `/api/departments/`
  - **Description**: List departments (filtered by user role)
  - **Permissions**: Staff or students
  - **Response**: List of departments with HOD and statistics

- **POST** `/api/departments/create/`
  - **Description**: Create a new department
  - **Permissions**: Superuser or principal
  - **Request Body**:
    ```json
    {
      "name": "string",
      "code": "string",
      "college": "integer"
    }
    ```

- **GET** `/api/departments/<id>/`
  - **Description**: Get department details
  - **Permissions**: Department management permission
  - **Response**: Department details with HOD and statistics

- **PUT/PATCH** `/api/departments/<id>/`
  - **Description**: Update department details
  - **Permissions**: Department management permission

- **DELETE** `/api/departments/<id>/`
  - **Description**: Delete department
  - **Permissions**: Department management permission

### User Registration
- **POST** `/api/register/`
  - **Description**: Register new users (students, faculty, HOD, principal)
  - **Permissions**: Allow any (for registration)
  - **Request Body**:
    ```json
    {
      "email": "string",
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "password": "string",
      "password_confirm": "string",
      "college_id": "integer",
      "department_id": "integer", // optional for students
      "role": "student|faculty|hod|principal"
    }
    ```

## Student Endpoints

### Profile Management
- **POST** `/api/student-profile/`
  - **Description**: Create student profile
  - **Permissions**: Student
  - **Request Body**:
    ```json
    {
      "student_id": "string",
      "year_of_admission": "integer",
      "course": "string",
      "branch": "string",
      "department_id": "integer",
      "phone_number": "string",
      "date_of_birth": "date"
    }
    ```

- **GET** `/api/student-profile/me/`
  - **Description**: Get own student profile
  - **Permissions**: Student
  - **Response**: Student profile details

- **PUT/PATCH** `/api/student-profile/me/`
  - **Description**: Update own student profile
  - **Permissions**: Student

### Permission Requests
- **GET** `/api/permission-requests/`
  - **Description**: List own permission requests
  - **Permissions**: Student
  - **Response**: List of permission requests

- **POST** `/api/permission-requests/`
  - **Description**: Create new permission request
  - **Permissions**: Student
  - **Request Body**:
    ```json
    {
      "request_type": "leave|event|other",
      "title": "string",
      "description": "string",
      "start_date": "date",
      "end_date": "date",
      "supporting_documents": "file" // optional
    }
    ```

- **GET** `/api/permission-requests/<id>/`
  - **Description**: Get permission request details
  - **Permissions**: Student or staff
  - **Response**: Permission request details

- **PUT/PATCH** `/api/permission-requests/<id>/`
  - **Description**: Update permission request (if pending)
  - **Permissions**: Student

### Achievements
- **GET** `/api/achievements/`
  - **Description**: List own achievements
  - **Permissions**: Student
  - **Response**: List of achievements

- **POST** `/api/achievements/`
  - **Description**: Create new achievement
  - **Permissions**: Student
  - **Request Body**:
    ```json
    {
      "title": "string",
      "description": "string",
      "category": "academic|sports|cultural|other",
      "date_achieved": "date",
      "evidence_file": "file" // optional
    }
    ```

- **GET** `/api/achievements/<id>/`
  - **Description**: Get achievement details
  - **Permissions**: Student or staff
  - **Response**: Achievement details

### Portfolio
- **GET** `/api/portfolio/download/`
  - **Description**: Download student portfolio PDF
  - **Permissions**: Student
  - **Response**: PDF file

## Principal Endpoints

### Dashboard
- **GET** `/api/principal/dashboard/`
  - **Description**: Get principal dashboard data
  - **Permissions**: Principal
  - **Response**: Dashboard statistics and lists

### Event Management
- **GET** `/api/principal/events/`
  - **Description**: List events in college
  - **Permissions**: Principal
  - **Response**: List of events

- **POST** `/api/principal/events/`
  - **Description**: Create new event
  - **Permissions**: Principal
  - **Request Body**:
    ```json
    {
      "name": "string",
      "description": "string",
      "start_date": "datetime",
      "end_date": "datetime",
      "target_years": ["integer"],
      "target_departments": ["integer"],
      "circular_photo": "file" // optional
    }
    ```

- **GET** `/api/principal/events/<id>/`
  - **Description**: Get event details
  - **Permissions**: Principal
  - **Response**: Event details

- **PUT/PATCH** `/api/principal/events/<id>/`
  - **Description**: Update event
  - **Permissions**: Principal

- **DELETE** `/api/principal/events/<id>/`
  - **Description**: Delete event
  - **Permissions**: Principal

### Event Permission Requests
- **POST** `/api/principal/event-permission-requests/<request_id>/approve/`
  - **Description**: Approve/reject event permission requests
  - **Permissions**: Principal
  - **Request Body**:
    ```json
    {
      "status": "approved|rejected",
      "rejection_reason": "string" // optional
    }
    ```

### HOD Management
- **GET** `/api/hods/`
  - **Description**: List HODs in college
  - **Permissions**: Principal
  - **Response**: List of HODs

- **POST** `/api/hods/create/`
  - **Description**: Create new HOD
  - **Permissions**: Principal
  - **Request Body**: Same as user registration with role="hod"

- **GET** `/api/hods/<id>/`
  - **Description**: Get HOD details
  - **Permissions**: Principal
  - **Response**: HOD user details

- **PUT/PATCH** `/api/hods/<id>/`
  - **Description**: Update HOD details
  - **Permissions**: Principal

- **DELETE** `/api/hods/<id>/`
  - **Description**: Remove HOD
  - **Permissions**: Principal

### Faculty Management
- **GET** `/api/faculty/`
  - **Description**: List faculty in college
  - **Permissions**: Principal
  - **Response**: List of faculty

- **POST** `/api/faculty/create/`
  - **Description**: Create new faculty
  - **Permissions**: Principal
  - **Request Body**: Same as user registration with role="faculty"

- **GET** `/api/faculty/<id>/`
  - **Description**: Get faculty details
  - **Permissions**: Principal
  - **Response**: Faculty user details

- **PUT/PATCH** `/api/faculty/<id>/`
  - **Description**: Update faculty details
  - **Permissions**: Principal

- **DELETE** `/api/faculty/<id>/`
  - **Description**: Remove faculty
  - **Permissions**: Principal

## HOD Endpoints

### Faculty Management
- **GET** `/api/faculty/`
  - **Description**: List faculty in department
  - **Permissions**: HOD
  - **Response**: List of faculty in department

- **POST** `/api/faculty/create/`
  - **Description**: Create new faculty in department
  - **Permissions**: HOD
  - **Request Body**: Same as user registration with role="faculty"

- **GET** `/api/faculty/<id>/`
  - **Description**: Get faculty details
  - **Permissions**: HOD
  - **Response**: Faculty user details

- **PUT/PATCH** `/api/faculty/<id>/`
  - **Description**: Update faculty details
  - **Permissions**: HOD

- **DELETE** `/api/faculty/<id>/`
  - **Description**: Remove faculty
  - **Permissions**: HOD

### Permission Requests Management
- **GET** `/api/permission-requests/pending/`
  - **Description**: List pending permission requests in department
  - **Permissions**: HOD
  - **Response**: List of pending permission requests

- **POST** `/api/permission-requests/<permission_id>/approve/`
  - **Description**: Approve/reject permission requests
  - **Permissions**: HOD
  - **Request Body**:
    ```json
    {
      "status": "approved|rejected",
      "rejection_reason": "string" // optional
    }
    ```

### Achievement Management
- **GET** `/api/achievements/pending/`
  - **Description**: List pending achievements in department
  - **Permissions**: HOD
  - **Response**: List of pending achievements

- **POST** `/api/achievements/<achievement_id>/approve/`
  - **Description**: Approve/reject achievements
  - **Permissions**: HOD
  - **Request Body**:
    ```json
    {
      "status": "approved|rejected",
      "rejection_reason": "string" // optional
    }
    ```

### Event Management
- **GET** `/api/principal/events/`
  - **Description**: List events (HOD can create events that need approval)
  - **Permissions**: HOD
  - **Response**: List of events

- **POST** `/api/principal/events/`
  - **Description**: Create new event (requires principal approval)
  - **Permissions**: HOD
  - **Request Body**: Same as principal event creation

## Faculty Endpoints

### Profile Management
- **POST** `/api/faculty-profile/`
  - **Description**: Create faculty profile
  - **Permissions**: Faculty
  - **Request Body**:
    ```json
    {
      "employee_id": "string",
      "department_id": "integer",
      "phone_number": "string",
      "office_location": "string"
    }
    ```

- **GET** `/api/faculty-profile/me/`
  - **Description**: Get own faculty profile
  - **Permissions**: Faculty
  - **Response**: Faculty profile details

- **PUT/PATCH** `/api/faculty-profile/me/`
  - **Description**: Update own faculty profile
  - **Permissions**: Faculty

### Permission Requests Management
- **GET** `/api/permission-requests/pending/`
  - **Description**: List pending permission requests in department
  - **Permissions**: Faculty
  - **Response**: List of pending permission requests

- **POST** `/api/permission-requests/<permission_id>/approve/`
  - **Description**: Approve/reject permission requests
  - **Permissions**: Faculty
  - **Request Body**:
    ```json
    {
      "status": "approved|rejected",
      "rejection_reason": "string" // optional
    }
    ```

### Achievement Management
- **GET** `/api/achievements/pending/`
  - **Description**: List pending achievements in department
  - **Permissions**: Faculty
  - **Response**: List of pending achievements

- **POST** `/api/achievements/<achievement_id>/approve/`
  - **Description**: Approve/reject achievements
  - **Permissions**: Faculty
  - **Request Body**:
    ```json
    {
      "status": "approved|rejected",
      "rejection_reason": "string" // optional
    }
    ```

## Bulk Operations

### Student Bulk Upload
- **POST** `/api/students/excel-upload/`
  - **Description**: Bulk upload students via Excel file
  - **Permissions**: Staff with student management permission
  - **Request Body**:
    ```
    file: Excel file
    college_id: integer
    department_id: integer
    ```
  - **Response**: Upload results with success/error details

- **GET** `/api/students/excel-template/`
  - **Description**: Download Excel template for student upload
  - **Permissions**: Staff with student management permission
  - **Response**: Excel template file

## User Profile

### Current User Details
- **GET** `/api/me/`
  - **Description**: Get current user details
  - **Permissions**: Authenticated user
  - **Response**: User details with role and profile information

## Notes

- All endpoints require appropriate authentication via JWT tokens
- File uploads use multipart/form-data encoding
- Date fields use ISO 8601 format (YYYY-MM-DD)
- DateTime fields use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- Pagination is available on list endpoints
- Error responses follow standard HTTP status codes with detailed error messages
- Permissions are enforced at the view level using custom permission classes
