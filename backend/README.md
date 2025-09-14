# Smart Student Hub - Backend

A Django REST API backend for the Smart Student Hub, a multi-tenant student achievement management platform.

## Features

- **Multi-tenant Architecture**: Support for multiple colleges with data isolation
- **Role-based Authentication**: Students, Faculty, and Organizers with different permissions
- **Achievement Management**: Students can submit achievements with evidence files
- **Approval Workflow**: Faculty can approve/reject student achievements
- **PDF Portfolio Generation**: Students can download their approved achievements as a PDF
- **JWT Authentication**: Secure token-based authentication
- **File Upload Support**: Evidence files for achievements

## Technology Stack

- **Framework**: Django 5.2.6
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **PDF Generation**: ReportLab
- **File Storage**: Local filesystem (configurable for cloud storage)

## Installation

1. **Clone the repository and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   - Create a database named `smart_student_hub`
   - Update database credentials in `smart_student_hub/settings.py` if needed

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create sample data (optional)**
   ```bash
   python manage.py setup_sample_data
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Login (get JWT tokens)
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/register/` - User registration

### Colleges
- `GET /api/colleges/` - List all colleges

### User Management
- `GET /api/me/` - Get current user details
- `PUT /api/me/` - Update current user details

### Student Profile
- `POST /api/student-profile/` - Create student profile
- `GET /api/student-profile/me/` - Get student profile
- `PUT /api/student-profile/me/` - Update student profile

### Faculty Profile
- `POST /api/faculty-profile/` - Create faculty profile
- `GET /api/faculty-profile/me/` - Get faculty profile
- `PUT /api/faculty-profile/me/` - Update faculty profile

### Achievements
- `GET /api/achievements/` - List achievements (student's own or all for faculty)
- `POST /api/achievements/` - Create new achievement
- `GET /api/achievements/{id}/` - Get achievement details
- `PUT /api/achievements/{id}/` - Update achievement (faculty only)
- `DELETE /api/achievements/{id}/` - Delete achievement
- `GET /api/achievements/pending/` - List pending achievements (faculty only)
- `POST /api/achievements/{id}/approve/` - Approve/reject achievement (faculty only)

### Portfolio
- `GET /api/portfolio/download/` - Download student portfolio PDF

## Sample Data

The `setup_sample_data` management command creates:
- Sample colleges (MIT, Stanford)
- Admin user: `admin@example.com` (password: `admin123`)
- Sample student: `student@example.com` (password: `student123`)
- Sample faculty: `faculty@example.com` (password: `faculty123`)

## Multi-tenancy

The system implements a "Shared Database, Shared Schema" multi-tenancy approach:
- Each user belongs to a college (tenant)
- All data is automatically filtered by the user's college
- Custom managers ensure data isolation
- Middleware sets the current college context

## File Uploads

Evidence files are stored in the `media/achievements/` directory. Supported formats:
- PDF documents
- Images (JPG, JPEG, PNG)
- Word documents (DOC, DOCX)

## PDF Portfolio Generation

Students can download a comprehensive PDF portfolio containing:
- Student information
- All approved achievements with details
- Professional formatting with college branding

## Development

### Project Structure
```
backend/
├── core/                    # Main Django app
│   ├── management/         # Custom management commands
│   ├── migrations/         # Database migrations
│   ├── models.py          # Database models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django admin configuration
│   ├── managers.py        # Custom model managers
│   ├── middleware.py      # Multi-tenancy middleware
│   └── pdf_utils.py       # PDF generation utilities
├── smart_student_hub/     # Django project settings
├── media/                 # File uploads
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

### Key Models
- **College**: Tenant model for multi-tenancy
- **User**: Custom user model with college association
- **StudentProfile**: Extended student information
- **FacultyProfile**: Extended faculty information
- **Achievement**: Student achievements with approval workflow

### Security Features
- JWT authentication with refresh tokens
- Role-based permissions
- Multi-tenant data isolation
- File upload validation
- CSRF protection

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings
2. Configure proper database credentials
3. Set up static file serving
4. Configure media file serving
5. Use environment variables for sensitive settings
6. Set up proper logging
7. Configure HTTPS

## Contributing

1. Follow Django best practices
2. Write tests for new features
3. Update documentation
4. Ensure multi-tenancy is maintained
5. Follow the existing code style

## License

This project is part of the Smart Student Hub system.
