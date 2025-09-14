from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import College, User, StudentProfile, FacultyProfile, Achievement
from .serializers import (
    CollegeSerializer, UserRegistrationSerializer, UserSerializer,
    StudentProfileSerializer, FacultyProfileSerializer, 
    AchievementSerializer, AchievementCreateSerializer, AchievementUpdateSerializer
)
from .pdf_utils import generate_student_portfolio, create_pdf_response


class CollegeListView(generics.ListAPIView):
    """API view to list all colleges"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.AllowAny]


class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create profile based on user role
        if user.is_student:
            # Student profile will be created separately via API
            pass
        elif user.is_faculty:
            # Faculty profile will be created separately via API
            pass
        
        return Response({
            'message': 'User created successfully',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """API view for user details"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class StudentProfileCreateView(generics.CreateAPIView):
    """API view for creating student profile"""
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentProfileDetailView(generics.RetrieveUpdateAPIView):
    """API view for student profile details"""
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        if not hasattr(self.request.user, 'student_profile'):
            raise generics.NotFound("Student profile not found")
        return self.request.user.student_profile


class FacultyProfileCreateView(generics.CreateAPIView):
    """API view for creating faculty profile"""
    serializer_class = FacultyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FacultyProfileDetailView(generics.RetrieveUpdateAPIView):
    """API view for faculty profile details"""
    serializer_class = FacultyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        if not hasattr(self.request.user, 'faculty_profile'):
            raise generics.NotFound("Faculty profile not found")
        return self.request.user.faculty_profile


class AchievementListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating achievements"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AchievementCreateSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        # Students can only see their own achievements
        if hasattr(self.request.user, 'student_profile'):
            return Achievement.objects.filter(student=self.request.user.student_profile)
        # Faculty can see all achievements in their college
        elif self.request.user.is_faculty:
            return Achievement.objects.for_tenant(self.request.user.college)
        return Achievement.objects.none()
    
    def perform_create(self, serializer):
        # This is handled in the serializer
        pass


class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for achievement details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AchievementUpdateSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        # Students can only access their own achievements
        if hasattr(self.request.user, 'student_profile'):
            return Achievement.objects.filter(student=self.request.user.student_profile)
        # Faculty can access all achievements in their college
        elif self.request.user.is_faculty:
            return Achievement.objects.for_tenant(self.request.user.college)
        return Achievement.objects.none()


class PendingAchievementsView(generics.ListAPIView):
    """API view for faculty to see pending achievements"""
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_faculty:
            return Achievement.objects.none()
        return Achievement.objects.pending_for_tenant(self.request.user.college)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_achievement(request, achievement_id):
    """API view for faculty to approve/reject achievements"""
    if not request.user.is_faculty:
        return Response({'error': 'Only faculty can approve achievements'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        achievement = Achievement.objects.for_tenant(request.user.college).get(id=achievement_id)
    except Achievement.DoesNotExist:
        return Response({'error': 'Achievement not found'}, status=status.HTTP_404_NOT_FOUND)
    
    status_value = request.data.get('status')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if status_value not in ['approved', 'rejected']:
        return Response({'error': 'Status must be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)
    
    achievement.status = status_value
    achievement.approved_by = request.user
    achievement.approved_at = timezone.now()
    
    if status_value == 'rejected':
        achievement.rejection_reason = rejection_reason
    
    achievement.save()
    
    serializer = AchievementSerializer(achievement)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_portfolio(request):
    """API view for students to download their portfolio PDF"""
    if not hasattr(request.user, 'student_profile'):
        return Response({'error': 'Only students can download portfolios'}, status=status.HTTP_403_FORBIDDEN)
    
    student_profile = request.user.student_profile
    
    # Generate PDF
    try:
        pdf_content = generate_student_portfolio(student_profile)
        
        # Create filename
        filename = f"{student_profile.student_id}_portfolio.pdf"
        
        # Return PDF response
        return create_pdf_response(pdf_content, filename)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate portfolio: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
