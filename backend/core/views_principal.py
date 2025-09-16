from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Department, User, Event, PermissionRequest
from .serializers import (
    DepartmentSerializer, UserSerializer, 
    EventSerializer, PermissionRequestSerializer
)
from .permissions import IsPrincipal


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsPrincipal]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(college=user.college)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, college=self.request.user.college)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsPrincipal]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(college=user.college)


class PrincipalDashboardView(APIView):
    permission_classes = [IsPrincipal]

    def get(self, request):
        user = request.user
        college = user.college

        hods = User.objects.filter(role='hod', college=college)
        faculty = User.objects.filter(role='faculty', college=college)
        events = Event.objects.filter(college=college)
        permissions = PermissionRequest.objects.filter(student__department__college=college)

        hods_data = UserSerializer(hods, many=True).data
        faculty_data = UserSerializer(faculty, many=True).data
        events_data = EventSerializer(events, many=True).data
        permissions_data = PermissionRequestSerializer(permissions, many=True).data

        return Response({
            'hods': hods_data,
            'faculty': faculty_data,
            'events': events_data,
            'permissions': permissions_data,
        }, status=status.HTTP_200_OK)
