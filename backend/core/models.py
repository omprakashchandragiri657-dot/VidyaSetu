# vidyasetu\backend\core\models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .managers import TenantManager, AchievementManager


class College(models.Model):
    """Tenant model for multi-tenancy - represents different colleges"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g., "MIT", "STANFORD"
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    principal = models.OneToOneField(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="principal_of_college",
        limit_choices_to={"is_principal": True},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Department(models.Model):
    """Department model within a college"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)  # e.g., "CSE", "ECE", "MECH"
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="departments")
    hod = models.OneToOneField(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod_of_department",
        limit_choices_to={"is_hod": True},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["code", "college"]

    def __str__(self):
        return f"{self.name} ({self.college.name})"


class User(AbstractUser):
    """Custom User model with hierarchical roles and college association"""
    ROLE_CHOICES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("hod", "Head of Department"),
        ("principal", "Principal"),
        ("superuser", "Superuser"),
    ]

    email = models.EmailField(unique=True)
    college = models.ForeignKey(
        College, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    # Role flags
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)
    is_hod = models.BooleanField(default=False)

    # Department association (for HOD & Faculty only)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="members"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["email"]

    def __str__(self):
        college_name = self.college.name if self.college else "No College"
        return f"{self.email} ({college_name}) - {self.get_role_display()}"

    def clean(self):
        # Email required
        if not self.email or self.email.strip() == "":
            raise ValidationError({"email": "Email field cannot be empty."})

        # College required for all except superuser
        if self.role != "superuser" and not self.college:
            raise ValidationError({"college": "College is required for this role."})

        # Department required for HOD & Faculty only
        if self.role in ["hod", "faculty"] and not self.department:
            raise ValidationError({"department": f"Department is required for {self.role} role."})

    def save(self, *args, **kwargs):
        self.clean()
        # Assign booleans based on role
        self.is_student = self.role == "student"
        self.is_faculty = self.role in ["faculty", "hod"]
        self.is_principal = self.role == "principal"
        self.is_hod = self.role == "hod"
        super().save(*args, **kwargs)

    def has_permission(self, action, target_user=None, target_department=None):
        """Permission hierarchy"""
        if self.is_superuser:
            return True

        if self.role == "principal":
            if target_user and target_user.college != self.college:
                return False
            if target_department and target_department.college != self.college:
                return False
            return True

        if self.role == "hod":
            if not self.department:
                return False
            if target_user and target_user.department != self.department:
                return False
            if target_department and target_department != self.department:
                return False
            return True

        if self.role == "faculty":
            if not self.department:
                return False
            if action in ["add_student", "edit_student"] and target_user:
                return target_user.department == self.department
            return False

        if self.role == "student":
            return action in ["upload_achievement", "download_profile_pdf", "request_permission"]

        return False


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50)  # College-specific student ID
    year_of_admission = models.IntegerField()
    course = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="students", null=True, blank=True
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)  # Keep address only for students
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_id"]
        unique_together = ["student_id", "department"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

    @property
    def profile_pdf_filename(self):
        return f"{self.user.username}_profile.pdf"


class FacultyProfile(models.Model):
    """Extended profile for faculty members"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    employee_id = models.CharField(max_length=50)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="faculty", null=True, blank=True
    )
    phone_number = models.CharField(max_length=15, blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["employee_id"]
        unique_together = ["employee_id", "department"]

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

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    date_achieved = models.DateField()
    evidence_file = models.FileField(
        upload_to="achievements/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png", "doc", "docx"])],
        help_text="Upload supporting documents (PDF, images, or documents)"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_achievements"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AchievementManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"

    @property
    def college(self):
        return self.student.user.college


class PermissionRequest(models.Model):
    """Model for student permission requests (leave, OD, etc.)"""
    REQUEST_TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('on_duty', 'On Duty'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="permission_requests"
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default="other")
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    supporting_documents = models.FileField(
        upload_to="permissions/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png", "doc", "docx"])],
        blank=True,
        null=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_permissions"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()} ({self.status})"


class Event(models.Model):
    """Model for college events created by HOD or Principal"""
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    target_years = models.JSONField(default=list, help_text="List of student years, e.g., [1, 2, 3]")
    target_departments = models.ManyToManyField(Department, related_name="events", blank=True)
    circular_photo = models.ImageField(upload_to="events/", blank=True, null=True, help_text="Upload hard copy circular photo (optional)")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_events",
        limit_choices_to={'role__in': ['hod', 'principal']}
    )
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_events",
        limit_choices_to={'role': 'principal'}
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.college.name} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.college_id and self.created_by.college:
            self.college = self.created_by.college
        if self.created_by.role == 'principal':
            self.status = 'approved'
            self.approved_by = self.created_by
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)

        # Create permission request if created by HOD
        if self.created_by.role == 'hod' and not hasattr(self, 'permission_request'):
            EventPermissionRequest.objects.create(
                event=self,
                requested_by=self.created_by
            )


class EventPermissionRequest(models.Model):
    """Model for event permission requests from HOD to principal"""
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="permission_request")
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_permission_requests")
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_event_requests")
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Event Permission Request for {self.event.name} by {self.requested_by.get_full_name()}"


class Notification(models.Model):
    """Model for notifications sent to users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
