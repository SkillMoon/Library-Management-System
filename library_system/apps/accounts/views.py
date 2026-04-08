from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


@login_required(login_url='/accounts/login/')
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    role = request.user.role
    templates = {
        'admin': 'accounts/dashboard_admin.html',
        'librarian': 'accounts/dashboard_librarian.html',
        'student': 'accounts/dashboard_student.html',
        'professor': 'accounts/dashboard_professor.html',
    }
    template = templates.get(role, 'accounts/dashboard_student.html')
    return render(request, template, {'user': request.user})
