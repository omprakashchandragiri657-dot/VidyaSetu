from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import College, User, StudentProfile, FacultyProfile, Achievement


class CollegeSerializer(serializers.ModelSerializer):
    """Serializer for College model"""
    
    class Meta:
        model = College
        fields = ['id', 'name', 'code', 'address', 'contact_email', 'contact_phone']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    college_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'college_id', 'is_student', 'is_faculty', 'is_organizer']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_college_id(self, value):
        try:
            College.objects.get(id=value)
        except College.DoesNotExist:
            raise serializers.ValidationError("Invalid college ID")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        college_id = validated_data.pop('college_id')
        college = College.objects.get(id=college_id)
        
        user = User.objects.create_user(
            college=college,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    college = CollegeSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'college', 'is_student', 'is_faculty', 'is_organizer', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'student_id', 'year_of_admission', 'course', 'branch', 'phone_number', 'date_of_birth', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FacultyProfileSerializer(serializers.ModelSerializer):
    """Serializer for FacultyProfile model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = FacultyProfile
        fields = ['id', 'user', 'employee_id', 'department', 'designation', 'phone_number', 'office_location', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model"""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'title', 'description', 'category', 'date_achieved', 
            'evidence_file', 'status', 'student_name', 'college_name',
            'approved_by_name', 'approved_at', 'rejection_reason', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'approved_by_name', 'approved_at', 'rejection_reason', 'created_at', 'updated_at']


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
