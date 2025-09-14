from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import College, Department, User, StudentProfile, FacultyProfile, Achievement, PermissionRequest


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'principal', 'contact_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'contact_email']
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'college', 'hod', 'created_at']
    list_filter = ['college', 'created_at']
    search_fields = ['name', 'code', 'college__name']
    ordering = ['college', 'name']


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'


class FacultyProfileInline(admin.StackedInline):
    model = FacultyProfile
    can_delete = False
    verbose_name_plural = 'Faculty Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline, FacultyProfileInline)
    list_display = ['email', 'username', 'college', 'role', 'is_student', 'is_faculty', 'is_organizer', 'is_active', 'created_at']
    list_filter = ['college', 'role', 'is_student', 'is_faculty', 'is_organizer', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']
    
    # Override the fieldsets to include email field properly
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('College Information', {'fields': ('college',)}),
        ('Role Information', {'fields': ('role', 'department', 'is_student', 'is_faculty', 'is_organizer', 'is_principal', 'is_hod')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    # Override add_fieldsets for user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'college', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make college field optional for superusers
        if obj and obj.is_superuser:
            form.base_fields['college'].required = False
        return form
    
    def save_model(self, request, obj, form, change):
        """Override save to handle role-based field updates"""
        # Set role-based boolean fields
        if obj.role == 'student':
            obj.is_student = True
            obj.is_faculty = False
            obj.is_principal = False
            obj.is_hod = False
        elif obj.role == 'faculty':
            obj.is_student = False
            obj.is_faculty = True
            obj.is_principal = False
            obj.is_hod = False
        elif obj.role == 'hod':
            obj.is_student = False
            obj.is_faculty = True
            obj.is_principal = False
            obj.is_hod = True
        elif obj.role == 'principal':
            obj.is_student = False
            obj.is_faculty = True
            obj.is_principal = True
            obj.is_hod = False
        elif obj.role == 'superuser':
            obj.is_student = False
            obj.is_faculty = False
            obj.is_principal = False
            obj.is_hod = False
        
        super().save_model(request, obj, form, change)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'course', 'branch', 'department', 'year_of_admission']
    list_filter = ['course', 'branch', 'department', 'year_of_admission', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    ordering = ['student_id']


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'designation']
    list_filter = ['department', 'designation', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'employee_id']
    ordering = ['employee_id']


@admin.register(PermissionRequest)
class PermissionRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'request_type', 'status', 'created_at']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['title', 'student__user__email', 'student__user__first_name', 'student__user__last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'request_type', 'title', 'description', 'start_date', 'end_date', 'supporting_documents')
        }),
        ('Approval Information', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'category', 'status', 'date_achieved', 'created_at']
    list_filter = ['status', 'category', 'date_achieved', 'created_at']
    search_fields = ['title', 'student__user__email', 'student__user__first_name', 'student__user__last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'title', 'description', 'category', 'date_achieved', 'evidence_file')
        }),
        ('Approval Information', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        """Filter achievements by the current user's college"""
        qs = super().get_queryset(request)
        if hasattr(request, 'current_college') and request.current_college:
            return qs.filter(student__user__college=request.current_college)
        return qs
