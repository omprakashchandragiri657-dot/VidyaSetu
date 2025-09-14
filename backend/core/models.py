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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom User model with college association for multi-tenancy"""
    email = models.EmailField(unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='users')
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_organizer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'college']
    
    class Meta:
        ordering = ['email']
    
    def __str__(self):
        return f"{self.email} ({self.college.name})"


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)  # College-specific student ID
    year_of_admission = models.IntegerField()
    course = models.CharField(max_length=100)  # e.g., "Computer Science", "Engineering"
    branch = models.CharField(max_length=100, blank=True)  # e.g., "CSE", "ECE"
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class FacultyProfile(models.Model):
    """Extended profile for faculty members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)  # e.g., "Professor", "Assistant Professor"
    phone_number = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


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
