from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from .models import College, Department, User, StudentProfile, FacultyProfile, Achievement, PermissionRequest
from .serializers import (
    CollegeSerializer, DepartmentSerializer, UserRegistrationSerializer, UserSerializer,
    StudentProfileSerializer, FacultyProfileSerializer, 
    AchievementSerializer, AchievementCreateSerializer, AchievementUpdateSerializer,
    PermissionRequestSerializer, PermissionRequestCreateSerializer, PermissionRequestUpdateSerializer
)
from .pdf_utils import generate_student_portfolio, create_pdf_response
from .permissions import (
    IsSuperUser, IsPrincipal, IsHOD, IsFaculty, IsStudent, IsStaffOrStudent,
    CanManageCollege, CanManageDepartment, CanManageStudents, CanApproveAchievements,
    CanApprovePermissions, IsOwnerOrStaff
)
from .excel_utils import process_student_excel, generate_student_excel_template


class CollegeListView(generics.ListAPIView):
    """API view to list all colleges"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.AllowAny]


class CollegeCreateView(generics.CreateAPIView):
    """API view for creating colleges (superuser only)"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [IsSuperUser]


class CollegeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for college details"""
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [CanManageCollege]


class DepartmentListView(generics.ListAPIView):
    """API view to list departments"""
    serializer_class = DepartmentSerializer
    permission_classes = [IsStaffOrStudent]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Department.objects.all()
        elif user.role == 'principal':
            return Department.objects.filter(college=user.college)
        elif user.role == 'hod':
            return Department.objects.filter(id=user.department.id)
        else:
            return Department.objects.filter(college=user.college)


class DepartmentCreateView(generics.CreateAPIView):
    """API view for creating departments (superuser or principal only)"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [CanManageCollege]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for department details"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [CanManageDepartment]


class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'User created successfully',
            'user_id': user.id,
            'role': user.role
        }, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """API view for user details"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class StudentListView(generics.ListAPIView):
    """API view to list students"""
    serializer_class = StudentProfileSerializer
    permission_classes = [CanManageStudents]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StudentProfile.objects.all()
        elif user.role == 'principal':
            return StudentProfile.objects.filter(department__college=user.college)
        elif user.role == 'hod':
            return StudentProfile.objects.filter(department=user.department)
        elif user.role == 'faculty':
            return StudentProfile.objects.filter(department=user.department)
        return StudentProfile.objects.none()


class StudentCreateView(generics.CreateAPIView):
    """API view for creating students"""
    serializer_class = StudentProfileSerializer
    permission_classes = [CanManageStudents]
    
    def perform_create(self, serializer):
        user = self.request.user
        department_id = self.request.data.get('department_id')
        
        # Validate department access
        if user.role == 'hod' and user.department.id != int(department_id):
            raise permissions.PermissionDenied("You can only add students to your department")
        elif user.role == 'faculty' and user.department.id != int(department_id):
            raise permissions.PermissionDenied("You can only add students to your department")
        
        serializer.save()


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for student details"""
    serializer_class = StudentProfileSerializer
    permission_classes = [CanManageStudents, IsOwnerOrStaff]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return StudentProfile.objects.all()
        elif user.role == 'principal':
            return StudentProfile.objects.filter(department__college=user.college)
        elif user.role == 'hod':
            return StudentProfile.objects.filter(department=user.department)
        elif user.role == 'faculty':
            return StudentProfile.objects.filter(department=user.department)
        return StudentProfile.objects.none()


class ExcelStudentUploadView(APIView):
    """API view for bulk student registration via Excel"""
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [CanManageStudents]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        college_id = request.data.get('college_id')
        department_id = request.data.get('department_id')
        
        if not college_id or not department_id:
            return Response({'error': 'College ID and Department ID are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Validate department access
        user = request.user
        if user.role == 'hod' and user.department.id != int(department_id):
            return Response({'error': 'You can only upload students to your department'}, 
                          status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'faculty' and user.department.id != int(department_id):
            return Response({'error': 'You can only upload students to your department'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        result = process_student_excel(file, college_id, department_id)
        
        if result['success']:
            return Response({
                'message': f"Successfully created {result['created_count']} students",
                'created_students': result['created_students'],
                'errors': result['errors']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)


class ExcelTemplateDownloadView(APIView):
    """API view to download Excel template"""
    permission_classes = [CanManageStudents]
    
    def get(self, request):
        import io
        import pandas as pd
        from django.http import HttpResponse
        
        df = generate_student_excel_template()
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Students', index=False)
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="student_template.xlsx"'
        return response


class StudentProfileCreateView(generics.CreateAPIView):
    """API view for creating student profile"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentProfileDetailView(generics.RetrieveUpdateAPIView):
    """API view for student profile details"""
    serializer_class = StudentProfileSerializer
    permission_classes = [IsStudent]
    
    def get_object(self):
        if not hasattr(self.request.user, 'student_profile'):
            raise generics.NotFound("Student profile not found")
        return self.request.user.student_profile


class PermissionRequestListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating permission requests"""
    permission_classes = [IsStaffOrStudent]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PermissionRequestCreateSerializer
        return PermissionRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return PermissionRequest.objects.filter(student=user.student_profile)
        elif user.role in ['faculty', 'hod', 'principal']:
            # Staff can see all permission requests in their college/department
            if user.role == 'principal':
                return PermissionRequest.objects.filter(student__department__college=user.college)
            else:
                return PermissionRequest.objects.filter(student__department=user.department)
        return PermissionRequest.objects.none()
    
    def perform_create(self, serializer):
        # This is handled in the serializer
        pass


class PermissionRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for permission request details"""
    permission_classes = [IsStaffOrStudent, IsOwnerOrStaff]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PermissionRequestUpdateSerializer
        return PermissionRequestSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return PermissionRequest.objects.filter(student=user.student_profile)
        elif user.role in ['faculty', 'hod', 'principal']:
            if user.role == 'principal':
                return PermissionRequest.objects.filter(student__department__college=user.college)
            else:
                return PermissionRequest.objects.filter(student__department=user.department)
        return PermissionRequest.objects.none()


class PendingPermissionRequestsView(generics.ListAPIView):
    """API view for staff to see pending permission requests"""
    serializer_class = PermissionRequestSerializer
    permission_classes = [CanApprovePermissions]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'principal':
            return PermissionRequest.objects.filter(
                student__department__college=user.college,
                status='pending'
            )
        else:
            return PermissionRequest.objects.filter(
                student__department=user.department,
                status='pending'
            )


class FacultyProfileCreateView(generics.CreateAPIView):
    """API view for creating faculty profile"""
    serializer_class = FacultyProfileSerializer
    permission_classes = [IsFaculty]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FacultyProfileDetailView(generics.RetrieveUpdateAPIView):
    """API view for faculty profile details"""
    serializer_class = FacultyProfileSerializer
    permission_classes = [IsFaculty]
    
    def get_object(self):
        if not hasattr(self.request.user, 'faculty_profile'):
            raise generics.NotFound("Faculty profile not found")
        return self.request.user.faculty_profile


class AchievementListCreateView(generics.ListCreateAPIView):
    """API view for listing and creating achievements"""
    permission_classes = [IsStaffOrStudent]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AchievementCreateSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Students can only see their own achievements
        if user.role == 'student':
            return Achievement.objects.filter(student=user.student_profile)
        # Staff can see all achievements in their college/department
        elif user.role == 'principal':
            return Achievement.objects.filter(student__department__college=user.college)
        elif user.role in ['hod', 'faculty']:
            return Achievement.objects.filter(student__department=user.department)
        return Achievement.objects.none()
    
    def perform_create(self, serializer):
        # This is handled in the serializer
        pass


class AchievementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for achievement details"""
    permission_classes = [IsStaffOrStudent, IsOwnerOrStaff]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AchievementUpdateSerializer
        return AchievementSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Students can only access their own achievements
        if user.role == 'student':
            return Achievement.objects.filter(student=user.student_profile)
        # Staff can access all achievements in their college/department
        elif user.role == 'principal':
            return Achievement.objects.filter(student__department__college=user.college)
        elif user.role in ['hod', 'faculty']:
            return Achievement.objects.filter(student__department=user.department)
        return Achievement.objects.none()


class PendingAchievementsView(generics.ListAPIView):
    """API view for staff to see pending achievements"""
    serializer_class = AchievementSerializer
    permission_classes = [CanApproveAchievements]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'principal':
            return Achievement.objects.filter(
                student__department__college=user.college,
                status='pending'
            )
        else:
            return Achievement.objects.filter(
                student__department=user.department,
                status='pending'
            )


@api_view(['POST'])
@permission_classes([CanApproveAchievements])
def approve_achievement(request, achievement_id):
    """API view for staff to approve/reject achievements"""
    user = request.user
    
    try:
        if user.role == 'principal':
            achievement = Achievement.objects.filter(
                student__department__college=user.college
            ).get(id=achievement_id)
        else:
            achievement = Achievement.objects.filter(
                student__department=user.department
            ).get(id=achievement_id)
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


@api_view(['POST'])
@permission_classes([CanApprovePermissions])
def approve_permission_request(request, permission_id):
    """API view for staff to approve/reject permission requests"""
    user = request.user
    
    try:
        if user.role == 'principal':
            permission_request = PermissionRequest.objects.filter(
                student__department__college=user.college
            ).get(id=permission_id)
        else:
            permission_request = PermissionRequest.objects.filter(
                student__department=user.department
            ).get(id=permission_id)
    except PermissionRequest.DoesNotExist:
        return Response({'error': 'Permission request not found'}, status=status.HTTP_404_NOT_FOUND)
    
    status_value = request.data.get('status')
    rejection_reason = request.data.get('rejection_reason', '')
    
    if status_value not in ['approved', 'rejected']:
        return Response({'error': 'Status must be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)
    
    permission_request.status = status_value
    permission_request.approved_by = request.user
    permission_request.approved_at = timezone.now()
    
    if status_value == 'rejected':
        permission_request.rejection_reason = rejection_reason
    
    permission_request.save()
    
    serializer = PermissionRequestSerializer(permission_request)
    return Response(serializer.data, status=status.HTTP_200_OK)


class HODListView(generics.ListAPIView):
    """API view to list HODs in the college"""
    serializer_class = UserSerializer
    permission_classes = [IsPrincipal]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(role='hod', college=user.college)


class HODCreateView(generics.CreateAPIView):
    """API view for creating HODs (principal only)"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsPrincipal]

    def perform_create(self, serializer):
        serializer.save()


class HODDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for HOD details (principal only)"""
    serializer_class = UserSerializer
    permission_classes = [IsPrincipal]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(role='hod', college=user.college)


class FacultyListView(generics.ListAPIView):
    """API view to list faculty in college/department"""
    serializer_class = UserSerializer
    permission_classes = [IsPrincipal, IsHOD]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'principal':
            return User.objects.filter(role='faculty', college=user.college)
        elif user.role == 'hod':
            return User.objects.filter(role='faculty', department=user.department)
        return User.objects.none()


class FacultyCreateView(generics.CreateAPIView):
    """API view for creating faculty (principal or HOD)"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsPrincipal, IsHOD]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'hod':
            # Ensure the department is the HOD's department
            serializer.validated_data['department_id'] = user.department.id
        serializer.save()


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API view for faculty details (principal or HOD)"""
    serializer_class = UserSerializer
    permission_classes = [IsPrincipal, IsHOD]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'principal':
            return User.objects.filter(role='faculty', college=user.college)
        elif user.role == 'hod':
            return User.objects.filter(role='faculty', department=user.department)
        return User.objects.none()


class UserLoginAPIView(APIView):
    """API view for user login (students, faculty, HOD, principal)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_superuser:
            return Response({'error': 'Superusers should use admin login'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class AdminLoginAPIView(APIView):
    """API view for admin login (superusers only)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_superuser:
            return Response({'error': 'Only superusers can access admin login'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


@api_view(['GET'])
@permission_classes([IsStudent])
def download_portfolio(request):
    """API view for students to download their portfolio PDF"""
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
