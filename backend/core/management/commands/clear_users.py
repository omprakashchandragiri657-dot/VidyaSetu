from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import College, Department, StudentProfile, FacultyProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Clear all user data including admins and users'

    def handle(self, *args, **options):
        # Clear principals and hods from colleges and departments
        College.objects.update(principal=None)
        Department.objects.update(hod=None)

        # Delete all profiles first to avoid integrity issues
        student_profiles_deleted = StudentProfile.objects.all().delete()
        faculty_profiles_deleted = FacultyProfile.objects.all().delete()

        # Delete all users
        users_deleted = User.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(f'Deleted {student_profiles_deleted[0]} student profiles')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {faculty_profiles_deleted[0]} faculty profiles')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Deleted {users_deleted[0]} users')
        )
        self.stdout.write(
            self.style.SUCCESS('All user data cleared successfully!')
        )
