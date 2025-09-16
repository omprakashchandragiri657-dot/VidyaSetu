from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import Department, User, Event, PermissionRequest, Notification, EventPermissionRequest
from .serializers import (
    DepartmentSerializer, UserSerializer,
    EventSerializer, PermissionRequestSerializer, EventPermissionRequestSerializer
)
from .permissions import IsPrincipal, IsHOD


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsPrincipal | IsHOD]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(college=user.college)

    def perform_create(self, serializer):
        event = serializer.save(created_by=self.request.user, college=self.request.user.college)
        # If created by HOD, create permission request
        if self.request.user.role == 'hod':
            EventPermissionRequest.objects.create(event=event, requested_by=self.request.user)


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


@method_decorator(login_required, name='dispatch')
class PrincipalDashboardTemplateView(APIView):
    """Template view for principal dashboard"""

    def get(self, request):
        user = request.user
        if user.role != 'principal':
            return Response({'error': 'Access denied'}, status=403)

        college = user.college

        hods = User.objects.filter(role='hod', college=college)
        faculty = User.objects.filter(role='faculty', college=college)
        events = Event.objects.filter(college=college)
        permissions = PermissionRequest.objects.filter(student__department__college=college)

        context = {
            'hods': hods,
            'faculty': faculty,
            'events': events,
            'permissions': permissions,
        }

        return render(request, 'core/principal_dashboard.html', context)


@api_view(['POST'])
@permission_classes([IsPrincipal])
def approve_event_permission_request(request, request_id):
    """API view for principal to approve/reject event permission requests"""
    user = request.user

    try:
        event_request = EventPermissionRequest.objects.filter(
            requested_by__college=user.college
        ).get(id=request_id)
    except EventPermissionRequest.DoesNotExist:
        return Response({'error': 'Event permission request not found'}, status=status.HTTP_404_NOT_FOUND)

    status_value = request.data.get('status')
    rejection_reason = request.data.get('rejection_reason', '')

    if status_value not in ['approved', 'rejected']:
        return Response({'error': 'Status must be approved or rejected'}, status=status.HTTP_400_BAD_REQUEST)

    event_request.status = status_value
    event_request.approved_by = request.user
    event_request.approved_at = timezone.now()

    if status_value == 'rejected':
        event_request.rejection_reason = rejection_reason

    event_request.save()

    # Update the event status accordingly
    if status_value == 'approved':
        event_request.event.status = 'approved'
        event_request.event.approved_by = request.user
        event_request.event.approved_at = timezone.now()
        event_request.event.save()
    elif status_value == 'rejected':
        event_request.event.status = 'rejected'
        event_request.event.rejection_reason = rejection_reason
        event_request.event.save()

    serializer = EventPermissionRequestSerializer(event_request)
    return Response(serializer.data, status=status.HTTP_200_OK)
