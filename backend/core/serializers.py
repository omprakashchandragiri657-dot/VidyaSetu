from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import College, Department, User, StudentProfile, FacultyProfile, Achievement, PermissionRequest, Event, EventPermissionRequest


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College model"""
    principal_name = serializers.CharField(source='principal.get_full_name', read_only=True)
    departments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = College
        fields = ['id', 'name', 'code', 'address', 'contact_email', 'contact_phone', 
                 'principal', 'principal_name', 'departments_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_departments_count(self, obj):
        return obj.departments.count()


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    college_name = serializers.CharField(source='college.name', read_only=True)
    hod_name = serializers.CharField(source='hod.get_full_name', read_only=True)
    students_count = serializers.SerializerMethodField()
    faculty_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'college', 'college_name', 'hod', 'hod_name',
                 'students_count', 'faculty_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_students_count(self, obj):
        return obj.students.count()
    
    def get_faculty_count(self, obj):
        return obj.faculty.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    college_id = serializers.IntegerField(write_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 
                 'college_id', 'department_id', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        role = attrs.get('role')
        department_id = attrs.get('department_id')
        
        # Validate department is required for certain roles
        if role in ['hod', 'faculty'] and not department_id:
            raise serializers.ValidationError(f"Department is required for {role} role")
        
        return attrs
    
    def validate_college_id(self, value):
        try:
            College.objects.get(id=value)
        except College.DoesNotExist:
            raise serializers.ValidationError("Invalid college ID")
        return value
    
    def validate_department_id(self, value):
        if value:
            try:
                Department.objects.get(id=value)
            except Department.DoesNotExist:
                raise serializers.ValidationError("Invalid department ID")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        college_id = validated_data.pop('college_id')
        department_id = validated_data.pop('department_id', None)
        college = College.objects.get(id=college_id)
        department = Department.objects.get(id=department_id) if department_id else None
        
        role = validated_data.get('role', 'student')
        
        # Use appropriate manager method based on role
        if role == 'principal':
            user = User.objects.create_principal(college=college, **validated_data)
        elif role == 'hod':
            user = User.objects.create_hod(college=college, department=department, **validated_data)
        elif role == 'faculty':
            user = User.objects.create_faculty(college=college, department=department, **validated_data)
        else:
            user = User.objects.create_student(college=college, **validated_data)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    college = CollegeSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'college', 'department',
                 'role', 'role_display', 'is_student', 'is_faculty', 'is_organizer', 
                 'is_principal', 'is_hod', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'student_id', 'year_of_admission', 'course', 'branch', 
                 'department', 'department_id', 'phone_number', 'date_of_birth', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_department_id(self, value):
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Invalid department ID")
        return value


class FacultyProfileSerializer(serializers.ModelSerializer):
    """Serializer for FacultyProfile model"""
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'employee_id', 'department', 'department_id', 'designation', 
                 'phone_number', 'office_location', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_department_id(self, value):
        try:
            Department.objects.get(id=value)
        except Department.DoesNotExist:
            raise serializers.ValidationError("Invalid department ID")
        return value


class PermissionRequestSerializer(serializers.ModelSerializer):
    """Serializer for PermissionRequest model"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    
    class Meta:
        model = PermissionRequest
        fields = [
            'id', 'request_type', 'request_type_display', 'title', 'description', 
            'start_date', 'end_date', 'supporting_documents', 'status', 'student_name', 
            'college_name', 'approved_by_name', 'approved_at', 'rejection_reason', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'approved_by_name', 'approved_at', 'rejection_reason', 'created_at', 'updated_at']


class PermissionRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating permission requests"""
    
    class Meta:
        model = PermissionRequest
        fields = ['request_type', 'title', 'description', 'start_date', 'end_date', 'supporting_documents']
    
    def create(self, validated_data):
        # Get the student profile from the authenticated user
        user = self.context['request'].user
        if not hasattr(user, 'student_profile'):
            raise serializers.ValidationError("User must have a student profile to create permission requests")
        
        validated_data['student'] = user.student_profile
        return super().create(validated_data)


class PermissionRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating permission request status (for faculty)"""
    
    class Meta:
        model = PermissionRequest
        fields = ['status', 'rejection_reason']
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        # Set approval information
        if validated_data.get('status') in ['approved', 'rejected']:
            instance.approved_by = self.context['request'].user
            instance.approved_at = timezone.now()
        
        return super().update(instance, validated_data)


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'title', 'description', 'category', 'category_display', 'date_achieved', 
            'evidence_file', 'status', 'student_name', 'college_name',
            'approved_by_name', 'approved_at', 'rejection_reason', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'approved_by_name', 'approved_at', 'rejection_reason', 'created_at', 'updated_at']


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'target_years', 'target_departments',
            'circular_photo', 'created_by', 'created_by_name', 'college', 'college_name', 'status',
            'approved_by', 'approved_at', 'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by_name', 'college_name', 'status', 'approved_by', 'approved_at', 'rejection_reason', 'created_at', 'updated_at']


class AchievementCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating achievements"""
    
    class Meta:
        model = Achievement
        fields = ['title', 'description', 'category', 'date_achieved', 'evidence_file']
    
    def create(self, validated_data):
        # Get the student profile from the authenticated user
        user = self.context['request'].user
        if not hasattr(user, 'student_profile'):
            raise serializers.ValidationError("User must have a student profile to create achievements")
        
        validated_data['student'] = user.student_profile
        return super().create(validated_data)


class AchievementUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating achievement status (for faculty)"""

    class Meta:
        model = Achievement
        fields = ['status', 'rejection_reason']

    def update(self, instance, validated_data):
        from django.utils import timezone

        # Set approval information
        if validated_data.get('status') in ['approved', 'rejected']:
            instance.approved_by = self.context['request'].user
            instance.approved_at = timezone.now()

        return super().update(instance, validated_data)


class EventPermissionRequestSerializer(serializers.ModelSerializer):
    """Serializer for EventPermissionRequest model"""
    event_name = serializers.CharField(source='event.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)

    class Meta:
        model = EventPermissionRequest
        fields = [
            'id', 'event', 'event_name', 'requested_by', 'requested_by_name', 'status',
            'approved_by', 'approved_at', 'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'approved_by', 'approved_at', 'created_at', 'updated_at']
