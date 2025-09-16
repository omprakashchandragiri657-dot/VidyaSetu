from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import College, Department, StudentProfile, FacultyProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create sample colleges
        college1, created = College.objects.get_or_create(
            code='MIT',
            defaults={
                'name': 'Massachusetts Institute of Technology',
                'address': '77 Massachusetts Ave, Cambridge, MA 02139',
                'contact_email': 'admin@mit.edu',
                'contact_phone': '+1-617-253-1000'
            }
        )

        college2, created = College.objects.get_or_create(
            code='STANFORD',
            defaults={
                'name': 'Stanford University',
                'address': '450 Serra Mall, Stanford, CA 94305',
                'contact_email': 'admin@stanford.edu',
                'contact_phone': '+1-650-723-2300'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created college: {college1.name}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created college: {college2.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'College already exists: {college1.name}')
            )
            self.stdout.write(
                self.style.WARNING(f'College already exists: {college2.name}')
            )

        # Create sample departments
        dept_cse, created = Department.objects.get_or_create(
            name='Computer Science',
            code='CSE',
            college=college1
        )
        dept_ece, created = Department.objects.get_or_create(
            name='Electronics and Communication',
            code='ECE',
            college=college1
        )

        # Create sample superuser
        if not User.objects.filter(email='admin@example.com').exists():
            admin_user = User.objects.create_superuser(
                email='admin@example.com',
                username='admin',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin@example.com (password: admin123)')
            )

        # Create sample principal
        if not User.objects.filter(email='principal@example.com').exists():
            principal_user = User.objects.create_user(
                email='principal@example.com',
                username='principal',
                password='principal123',
                college=college1,
                role='principal',
                first_name='Dr. Alice',
                last_name='Johnson',
                is_staff=True
            )
            college1.principal = principal_user
            college1.save()
            FacultyProfile.objects.create(
                user=principal_user,
                employee_id='MITP001',
                phone_number='+1-555-0789',
                office_location='Principal Office'
            )
            self.stdout.write(
                self.style.SUCCESS('Created sample principal: principal@example.com (password: principal123)')
            )

        # Create sample hod
        if not User.objects.filter(email='hod@example.com').exists():
            hod_user = User.objects.create_user(
                email='hod@example.com',
                username='hod',
                password='hod123',
                college=college1,
                role='hod',
                department=dept_cse,
                first_name='Prof. Bob',
                last_name='Williams',
                is_staff=True
            )
            dept_cse.hod = hod_user
            dept_cse.save()
            FacultyProfile.objects.create(
                user=hod_user,
                employee_id='MITH001',
                department=dept_cse,
                phone_number='+1-555-0345',
                office_location='HOD Office, CSE'
            )
            self.stdout.write(
                self.style.SUCCESS('Created sample hod: hod@example.com (password: hod123)')
            )

        # Create sample faculty
        if not User.objects.filter(email='faculty@example.com').exists():
            faculty_user = User.objects.create_user(
                email='faculty@example.com',
                username='faculty',
                password='faculty123',
                college=college1,
                role='faculty',
                department=dept_cse,
                first_name='Dr. Jane',
                last_name='Smith'
            )

            FacultyProfile.objects.create(
                user=faculty_user,
                employee_id='MITF001',
                department=dept_cse,
                phone_number='+1-555-0456',
                office_location='Building 32, Room 123'
            )

            self.stdout.write(
                self.style.SUCCESS('Created sample faculty: faculty@example.com (password: faculty123)')
            )

        # Create sample student
        if not User.objects.filter(email='student@example.com').exists():
            student_user = User.objects.create_user(
                email='student@example.com',
                username='student',
                password='student123',
                college=college1,
                role='student',
                department=dept_cse,
                first_name='John',
                last_name='Doe'
            )

            StudentProfile.objects.create(
                user=student_user,
                student_id='MIT2024001',
                year_of_admission=2024,
                course='Computer Science',
                branch='CSE',
                department=dept_cse,
                phone_number='+1-555-0123'
            )

            self.stdout.write(
                self.style.SUCCESS('Created sample student: student@example.com (password: student123)')
            )

        self.stdout.write(
            self.style.SUCCESS('Sample data setup completed!')
        )
