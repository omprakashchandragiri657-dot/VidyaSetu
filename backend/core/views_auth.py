from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


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
            tokens = get_tokens_for_user(user)
            response = redirect('principal-dashboard' if user.role == 'principal' else
                                'student-profile-detail' if user.role == 'student' else
                                'faculty-profile-detail' if user.role in ['faculty', 'hod'] else
                                'user-detail')
            response.set_cookie('access_token', tokens['access'], httponly=True)
            response.set_cookie('refresh_token', tokens['refresh'], httponly=True)
            return response
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
