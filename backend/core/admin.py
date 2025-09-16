from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import College, Department, User, StudentProfile, FacultyProfile, Achievement, PermissionRequest


# ------------------ Utility: Generate Student PDF ------------------
def generate_student_pdf(student):
    """Generate PDF for a single student and return as HttpResponse"""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.user.username}_profile.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 50

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Student Profile")
    y -= 40

    # Basic Info
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Name: {student.user.first_name} {student.user.last_name}")
    y -= 20
    p.drawString(50, y, f"Email: {student.user.email}")
    y -= 20
    p.drawString(50, y, f"College: {student.user.college.name}")
    y -= 20
    p.drawString(50, y, f"Department: {student.department.name if student.department else 'N/A'}")
    y -= 20
    p.drawString(50, y, f"Student ID: {student.student_id}")
    y -= 20
    p.drawString(50, y, f"Course: {student.course}")
    y -= 20
    p.drawString(50, y, f"Branch: {student.branch}")
    y -= 20
    p.drawString(50, y, f"Year of Admission: {student.year_of_admission}")

    p.showPage()
    p.save()
    return response


# ------------------ Admin Classes ------------------
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
    list_display = ['email', 'username', 'college', 'role', 'is_student', 'is_faculty',
                     'is_active', 'created_at']
    list_filter = ['college', 'role', 'is_student', 'is_faculty',
                    'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

    # Override the fieldsets to include role/college info
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('College Information', {'fields': ('college',)}),
        ('Role Information', {
            'fields': ('role', 'is_student', 'is_faculty',
                       'is_principal', 'is_hod')
        }),
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
            'fields': ('email', 'username', 'password1', 'password2', 'college', 'role', 'department'),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']

    def get_inlines(self, request, obj=None):
        """Return inlines based on the user's role"""
        if obj:
            if obj.role == 'student':
                return [StudentProfileInline]
            elif obj.role in ['faculty', 'hod', 'principal']:
                return [FacultyProfileInline]
        else:
            # For add form, show both inlines, JS will hide based on role
            return [StudentProfileInline, FacultyProfileInline]
        return []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make college optional for superusers
        if obj and obj.is_superuser:
            form.base_fields['college'].required = False
        return form

    def save_model(self, request, obj, form, change):
        """Role-based flag assignment"""
        if obj.role == 'student':
            obj.is_student, obj.is_faculty, obj.is_principal, obj.is_hod = True, False, False, False
        elif obj.role == 'faculty':
            obj.is_student, obj.is_faculty, obj.is_principal, obj.is_hod = False, True, False, False
        elif obj.role == 'hod':
            obj.is_student, obj.is_faculty, obj.is_principal, obj.is_hod = False, True, False, True
        elif obj.role == 'principal':
            obj.is_student, obj.is_faculty, obj.is_principal, obj.is_hod = False, True, True, False
        else:  # superuser or others
            obj.is_student, obj.is_faculty, obj.is_principal, obj.is_hod = False, False, False, False

        super().save_model(request, obj, form, change)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'course', 'branch', 'department', 'year_of_admission']
    list_filter = ['course', 'branch', 'department', 'year_of_admission', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'student_id']
    ordering = ['student_id']

    actions = ["download_student_pdf"]

    def download_student_pdf(self, request, queryset):
        """Download a student profile as PDF (role-based access)"""
        if queryset.count() == 1:
            student = queryset.first()
            user = request.user

            if user.is_superuser:
                return generate_student_pdf(student)
            elif user.role == "principal" and student.user.college == user.college:
                return generate_student_pdf(student)
            elif user.role == "hod" and hasattr(user, "facultyprofile") \
                    and student.department == user.facultyprofile.department:
                return generate_student_pdf(student)
            elif user.role == "faculty" and hasattr(user, "facultyprofile") \
                    and student.department == user.facultyprofile.department:
                return generate_student_pdf(student)
            else:
                self.message_user(request, "You don’t have permission to download this student’s profile.")
                return None
        else:
            self.message_user(request, "Please select exactly one student.")
            return None

    download_student_pdf.short_description = "Download Student Profile as PDF"


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'user_role', 'phone_number', 'office_location']
    list_filter = ['department', 'user__role', 'phone_number', 'office_location', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'employee_id']
    ordering = ['employee_id']

    def user_role(self, obj):
        return obj.user.get_role_display()
    user_role.short_description = 'Role'


@admin.register(PermissionRequest)
class PermissionRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'request_type', 'status', 'created_at']
    list_filter = ['request_type', 'status', 'created_at']
    search_fields = ['title', 'student__user__email', 'student__user__first_name', 'student__user__last_name']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'request_type', 'title', 'description',
                       'start_date', 'end_date', 'supporting_documents')
        }),
        ('Approval Information', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
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
            'fields': ('student', 'title', 'description', 'category',
                       'date_achieved', 'evidence_file')
        }),
        ('Approval Information', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_queryset(self, request):
        """Filter achievements by the current user's college if available"""
        qs = super().get_queryset(request)
        if hasattr(request, 'current_college') and request.current_college:
            return qs.filter(student__user__college=request.current_college)
        return qs
