from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import College, User, StudentProfile, FacultyProfile, Achievement


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_email', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'contact_email']
    ordering = ['name']


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
    list_display = ['email', 'username', 'college', 'is_student', 'is_faculty', 'is_organizer', 'is_active', 'created_at']
    list_filter = ['college', 'is_student', 'is_faculty', 'is_organizer', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('College Information', {'fields': ('college',)}),
        ('Role Information', {'fields': ('is_student', 'is_faculty', 'is_organizer')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'course', 'branch', 'year_of_admission']
    list_filter = ['course', 'branch', 'year_of_admission', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    ordering = ['student_id']


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'designation']
    list_filter = ['department', 'designation', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'employee_id']
    ordering = ['employee_id']


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
