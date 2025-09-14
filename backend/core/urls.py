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
    
    # User endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Student Profile endpoints
    path('student-profile/', views.StudentProfileCreateView.as_view(), name='student-profile-create'),
    path('student-profile/me/', views.StudentProfileDetailView.as_view(), name='student-profile-detail'),
    
    # Faculty Profile endpoints
    path('faculty-profile/', views.FacultyProfileCreateView.as_view(), name='faculty-profile-create'),
    path('faculty-profile/me/', views.FacultyProfileDetailView.as_view(), name='faculty-profile-detail'),
    
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
