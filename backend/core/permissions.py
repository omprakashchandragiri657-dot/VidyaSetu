from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):
    """Custom permission to only allow superusers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsPrincipal(permissions.BasePermission):
    """Custom permission to only allow principals."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'principal'


class IsHOD(permissions.BasePermission):
    """Custom permission to only allow HODs."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'hod'


class IsFaculty(permissions.BasePermission):
    """Custom permission to allow faculty and above."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['faculty', 'hod', 'principal']


class IsStudent(permissions.BasePermission):
    """Custom permission to only allow students."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsStaffOrStudent(permissions.BasePermission):
    """Custom permission to allow staff (faculty, HOD, principal) or students."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['student', 'faculty', 'hod', 'principal']


class CanManageCollege(permissions.BasePermission):
    """Permission to manage college (superuser or principal of that college)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role == 'principal'


class CanManageDepartment(permissions.BasePermission):
    """Permission to manage department (superuser, principal, or HOD of that department)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.role == 'principal':
            return True
        
        return request.user.role == 'hod'


class CanManageStudents(permissions.BasePermission):
    """Permission to manage students (superuser, principal, HOD, or faculty)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in ['principal', 'hod', 'faculty']


class CanApproveAchievements(permissions.BasePermission):
    """Permission to approve achievements (superuser, principal, HOD, or faculty)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in ['principal', 'hod', 'faculty']


class CanApprovePermissions(permissions.BasePermission):
    """Permission to approve permission requests (superuser, principal, HOD, or faculty)."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in ['principal', 'hod', 'faculty']


class IsOwnerOrStaff(permissions.BasePermission):
    """Permission to allow users to access their own data or staff to access any data."""
    
    def has_object_permission(self, request, view, obj):
        # Staff can access any object
        if request.user and request.user.is_authenticated and request.user.role in ['principal', 'hod', 'faculty']:
            return True
        
        # Users can access their own objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'student') and hasattr(obj.student, 'user'):
            return obj.student.user == request.user
        
        return False
