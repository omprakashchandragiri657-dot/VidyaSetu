from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render


class UserLoginView(View):
    template_name = 'core/user_login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_superuser:
                return redirect('admin-login')
            login(request, user)
            # Redirect based on user role
            if user.role == 'principal':
                return redirect('principal-dashboard')
            elif user.role == 'student':
                return redirect('student-profile-detail')
            elif user.role in ['faculty', 'hod']:
                return redirect('faculty-profile-detail')
            else:
                return redirect('user-detail')  # Fallback to user details
        return render(request, self.template_name, {'form': form, 'error': 'Invalid credentials'})


class AdminLoginView(View):
    template_name = 'core/admin_login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_superuser:
                return render(request, self.template_name, {'form': form, 'error': 'Only superusers can access admin login'})
            login(request, user)
            return redirect('/admin/')
        return render(request, self.template_name, {'form': form, 'error': 'Invalid credentials'})
