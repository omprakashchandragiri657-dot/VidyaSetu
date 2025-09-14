from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from .managers import TenantManager, AchievementManager


class College(models.Model):
    """Tenant model for multi-tenancy - represents different colleges"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., "MIT", "STANFORD"
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    principal = models.OneToOneField('User', on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='principal_of_college', limit_choices_to={'is_principal': True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Department model within a college"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)  # e.g., "CSE", "ECE", "MECH"
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='departments')
    hod = models.OneToOneField('User', on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='hod_of_department', limit_choices_to={'is_hod': True})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['code', 'college']
    
    def __str__(self):
        return f"{self.name} ({self.college.name})"


class User(AbstractUser):
    """Custom User model with hierarchical roles and college association"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'Head of Department'),
        ('principal', 'Principal'),
        ('superuser', 'Superuser'),
    ]
    
    email = models.EmailField(unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Legacy boolean fields for backward compatibility
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    
    # New role-based boolean fields
    is_principal = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)
    
    # Department association for HODs and Faculty
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='members')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['email']
    
    def __str__(self):
        college_name = self.college.name if self.college else "No College"
        return f"{self.email} ({college_name}) - {self.get_role_display()}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate email is not empty
        if not self.email or self.email.strip() == '':
            raise ValidationError({'email': 'Email field cannot be empty.'})
        
        # Validate college requirement for non-superusers
        if not self.is_superuser and not self.college:
            raise ValidationError({'college': 'College is required for non-superuser accounts.'})
        
        # Validate department requirement for HODs and faculty
        if self.role in ['hod', 'faculty'] and not self.department:
            raise ValidationError({'department': f'Department is required for {self.role} role.'})
    
    def save(self, *args, **kwargs):
        # Clean the model before saving
        self.clean()
        
        # Update boolean fields based on role
        if self.role == 'student':
            self.is_student = True
            self.is_faculty = False
            self.is_principal = False
            self.is_hod = False
        elif self.role == 'faculty':
            self.is_student = False
            self.is_faculty = True
            self.is_principal = False
            self.is_hod = False
        elif self.role == 'hod':
            self.is_student = False
            self.is_faculty = True  # HODs are also faculty
            self.is_principal = False
            self.is_hod = True
        elif self.role == 'principal':
            self.is_student = False
            self.is_faculty = True  # Principals are also faculty
            self.is_principal = True
            self.is_hod = False
        elif self.role == 'superuser':
            self.is_student = False
            self.is_faculty = False
            self.is_principal = False
            self.is_hod = False
        
        super().save(*args, **kwargs)
    
    def has_permission(self, action, target_user=None, target_department=None):
        """Check if user has permission for specific action"""
        if self.is_superuser:
            return True
        
        if self.role == 'principal':
            # Principal has full access within their college
            if not self.college:
                return False
            if target_user and target_user.college != self.college:
                return False
            if target_department and target_department.college != self.college:
                return False
            return True
        
        elif self.role == 'hod':
            # HOD has access within their department
            if not self.department:
                return False
            if target_user and hasattr(target_user, 'student_profile'):
                return target_user.student_profile.department == self.department
            if target_user and hasattr(target_user, 'faculty_profile'):
                return target_user.faculty_profile.department == self.department
            if target_department:
                return target_department == self.department
            return False
        
        elif self.role == 'faculty':
            # Faculty can only manage students in their department
            if not self.department:
                return False
            if action in ['add_student', 'edit_student'] and target_user:
                if hasattr(target_user, 'student_profile'):
                    return target_user.student_profile.department == self.department
            return False
        
        elif self.role == 'student':
            # Students have limited permissions
            return action in ['upload_achievement', 'download_portfolio', 'request_permission']
        
        return False


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50)  # College-specific student ID
    year_of_admission = models.IntegerField()
    course = models.CharField(max_length=100)  # e.g., "Computer Science", "Engineering"
    branch = models.CharField(max_length=100, blank=True)  # e.g., "CSE", "ECE"
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student_id']
        unique_together = ['student_id', 'department']  # Student ID unique within department
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class FacultyProfile(models.Model):
    """Extended profile for faculty members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty', null=True, blank=True)
    designation = models.CharField(max_length=100)  # e.g., "Professor", "Assistant Professor"
    phone_number = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee_id']
        unique_together = ['employee_id', 'department']  # Employee ID unique within department
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class PermissionRequest(models.Model):
    """Model for student permission requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('leave', 'Leave Request'),
        ('event', 'Event Participation'),
        ('project', 'Project Approval'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='permission_requests')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    supporting_documents = models.FileField(
        upload_to='permission_requests/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        blank=True,
        help_text="Upload supporting documents if required"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_permissions'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"
    
    @property
    def college(self):
        """Get the college through the student's user"""
        return self.student.user.college


class Achievement(models.Model):
    """Model for student achievements"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('extracurricular', 'Extracurricular'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('technical', 'Technical'),
        ('leadership', 'Leadership'),
        ('volunteer', 'Volunteer'),
        ('other', 'Other'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date_achieved = models.DateField()
    evidence_file = models.FileField(
        upload_to='achievements/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        help_text="Upload supporting documents (PDF, images, or documents)"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_achievements'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = AchievementManager()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"
    
    @property
    def college(self):
        """Get the college through the student's user"""
        return self.student.user.college
