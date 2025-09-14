import pandas as pd
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import User, StudentProfile, College, Department


def process_student_excel(file, college_id, department_id):
    """
    Process Excel file for bulk student registration
    
    Expected Excel format:
    - student_id: Student ID (required)
    - email: Email address (required)
    - username: Username (required)
    - first_name: First name (required)
    - last_name: Last name (required)
    - year_of_admission: Year of admission (required)
    - course: Course name (required)
    - branch: Branch name (optional)
    - phone_number: Phone number (optional)
    - date_of_birth: Date of birth in YYYY-MM-DD format (optional)
    """
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Validate required columns
        required_columns = ['student_id', 'email', 'username', 'first_name', 'last_name', 
                          'year_of_admission', 'course']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Get college and department
        try:
            college = College.objects.get(id=college_id)
            department = Department.objects.get(id=department_id)
        except (College.DoesNotExist, Department.DoesNotExist) as e:
            raise ValidationError(f"Invalid college or department: {str(e)}")
        
        # Process each row
        created_students = []
        errors = []
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Check if student already exists
                    if StudentProfile.objects.filter(
                        student_id=row['student_id'], 
                        department=department
                    ).exists():
                        errors.append(f"Row {index + 2}: Student ID {row['student_id']} already exists")
                        continue
                    
                    # Check if user with email already exists
                    if User.objects.filter(email=row['email']).exists():
                        errors.append(f"Row {index + 2}: Email {row['email']} already exists")
                        continue
                    
                    # Create user
                    user = User.objects.create_student(
                        email=row['email'],
                        username=row['username'],
                        college=college,
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )
                    
                    # Create student profile
                    student_profile = StudentProfile.objects.create(
                        user=user,
                        student_id=row['student_id'],
                        year_of_admission=int(row['year_of_admission']),
                        course=row['course'],
                        branch=row.get('branch', ''),
                        department=department,
                        phone_number=row.get('phone_number', ''),
                        date_of_birth=pd.to_datetime(row.get('date_of_birth'), errors='coerce').date() if pd.notna(row.get('date_of_birth')) else None
                    )
                    
                    created_students.append({
                        'student_id': student_profile.student_id,
                        'name': user.get_full_name(),
                        'email': user.email
                    })
                    
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
                    continue
        
        return {
            'success': True,
            'created_count': len(created_students),
            'created_students': created_students,
            'errors': errors
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'created_count': 0,
            'created_students': [],
            'errors': []
        }


def generate_student_excel_template():
    """
    Generate Excel template for student registration
    """
    template_data = {
        'student_id': ['STU001', 'STU002'],
        'email': ['student1@example.com', 'student2@example.com'],
        'username': ['student1', 'student2'],
        'first_name': ['John', 'Jane'],
        'last_name': ['Doe', 'Smith'],
        'year_of_admission': [2024, 2024],
        'course': ['Computer Science', 'Electronics'],
        'branch': ['CSE', 'ECE'],
        'phone_number': ['1234567890', '0987654321'],
        'date_of_birth': ['2000-01-01', '2000-02-02']
    }
    
    df = pd.DataFrame(template_data)
    return df
