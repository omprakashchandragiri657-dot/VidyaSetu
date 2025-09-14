from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.apps import apps


class TenantManager(BaseUserManager):
    """Custom manager for User model with email as username and college association"""

    def create_user(self, email, username, college=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        
        # Only non-superusers need a college
        if not extra_fields.get('is_superuser', False) and not college:
            raise ValueError("Non-superuser users must belong to a college")

        # 🔑 Fix circular import by lazy-loading College
        if college and isinstance(college, int):
            College = apps.get_model("core", "College")
            college = College.objects.get(pk=college)

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, college=college, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        # Superusers don't need a college
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "superuser")

        return self.create_user(email, username, college=None, password=password, **extra_fields)
    
    def create_principal(self, email, username, college, password=None, **extra_fields):
        """Create a principal user"""
        extra_fields.setdefault("role", "principal")
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, username, college, password, **extra_fields)
    
    def create_hod(self, email, username, college, department, password=None, **extra_fields):
        """Create a HOD user"""
        extra_fields.setdefault("role", "hod")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("department", department)
        return self.create_user(email, username, college, password, **extra_fields)
    
    def create_faculty(self, email, username, college, department, password=None, **extra_fields):
        """Create a faculty user"""
        extra_fields.setdefault("role", "faculty")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("department", department)
        return self.create_user(email, username, college, password, **extra_fields)
    
    def create_student(self, email, username, college, password=None, **extra_fields):
        """Create a student user"""
        extra_fields.setdefault("role", "student")
        extra_fields.setdefault("is_staff", False)
        return self.create_user(email, username, college, password, **extra_fields)


class AchievementManager(models.Manager):
    """Custom manager for achievements with tenant filtering"""

    def get_queryset(self):
        return super().get_queryset()

    def for_tenant(self, college):
        return self.get_queryset().filter(student__user__college=college)

    def pending_for_tenant(self, college):
        return self.for_tenant(college).filter(status="pending")

    def approved_for_tenant(self, college):
        return self.for_tenant(college).filter(status="approved")
