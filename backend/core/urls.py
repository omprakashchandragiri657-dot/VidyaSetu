from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

# Create a router for API endpoints
router = DefaultRouter()

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # College endpoints
    path('colleges/', views.CollegeListView.as_view(), name='college-list'),
    path('colleges/create/', views.CollegeCreateView.as_view(), name='college-create'),
    path('colleges/<int:pk>/', views.CollegeDetailView.as_view(), name='college-detail'),
    
    # Department endpoints
    path('departments/', views.DepartmentListView.as_view(), name='department-list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department-create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department-detail'),
    
    # User endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Student endpoints
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/excel-upload/', views.ExcelStudentUploadView.as_view(), name='excel-student-upload'),
    path('students/excel-template/', views.ExcelTemplateDownloadView.as_view(), name='excel-template-download'),
    
    # Student Profile endpoints
    path('student-profile/', views.StudentProfileCreateView.as_view(), name='student-profile-create'),
    path('student-profile/me/', views.StudentProfileDetailView.as_view(), name='student-profile-detail'),
    
    # Faculty Profile endpoints
    path('faculty-profile/', views.FacultyProfileCreateView.as_view(), name='faculty-profile-create'),
    path('faculty-profile/me/', views.FacultyProfileDetailView.as_view(), name='faculty-profile-detail'),
    
    # Permission Request endpoints
    path('permission-requests/', views.PermissionRequestListCreateView.as_view(), name='permission-request-list-create'),
    path('permission-requests/<int:pk>/', views.PermissionRequestDetailView.as_view(), name='permission-request-detail'),
    path('permission-requests/pending/', views.PendingPermissionRequestsView.as_view(), name='pending-permission-requests'),
    path('permission-requests/<int:permission_id>/approve/', views.approve_permission_request, name='approve-permission-request'),
    
    # Achievement endpoints
    path('achievements/', views.AchievementListCreateView.as_view(), name='achievement-list-create'),
    path('achievements/<int:pk>/', views.AchievementDetailView.as_view(), name='achievement-detail'),
    path('achievements/pending/', views.PendingAchievementsView.as_view(), name='pending-achievements'),
    path('achievements/<int:achievement_id>/approve/', views.approve_achievement, name='approve-achievement'),
    
    # Portfolio endpoints
    path('portfolio/download/', views.download_portfolio, name='download-portfolio'),
    
    # Include router URLs
    path('', include(router.urls)),
]
