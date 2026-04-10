from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import LoginForm, LibrarianForm, MemberForm, ProfileForm
from .models import User
from .decorators import role_required


# ─────────────────────────────────────────
# Auth Views
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('accounts:dashboard')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ─────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────

@login_required(login_url='/accounts/login/')
def dashboard_view(request):
    role = request.user.role
    templates = {
        'admin':     'accounts/dashboard_admin.html',
        'librarian': 'accounts/dashboard_librarian.html',
        'student':   'accounts/dashboard_student.html',
        'professor': 'accounts/dashboard_professor.html',
    }
    template = templates.get(role, 'accounts/dashboard_student.html')
    return render(request, template, {'user': request.user})


# ─────────────────────────────────────────
# Profile (FR04)
# ─────────────────────────────────────────

@login_required(login_url='/accounts/login/')
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت بروزرسانی شد.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# ─────────────────────────────────────────
# Librarian Management (FR01) — فقط admin
# ─────────────────────────────────────────

@login_required(login_url='/accounts/login/')
@role_required('admin')
def librarian_list(request):
    librarians = User.objects.filter(role=User.Role.LIBRARIAN).order_by('last_name')
    return render(request, 'accounts/librarian_list.html', {'librarians': librarians})


@login_required(login_url='/accounts/login/')
@role_required('admin')
def librarian_create(request):
    if request.method == 'POST':
        form = LibrarianForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کتابدار با موفقیت ایجاد شد.')
            return redirect('accounts:librarian_list')
    else:
        form = LibrarianForm()

    return render(request, 'accounts/librarian_form.html', {
        'form': form,
        'action': 'ایجاد کتابدار'
    })


@login_required(login_url='/accounts/login/')
@role_required('admin')
def librarian_edit(request, pk):
    librarian = get_object_or_404(User, pk=pk, role=User.Role.LIBRARIAN)
    if request.method == 'POST':
        form = LibrarianForm(request.POST, instance=librarian)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات کتابدار بروزرسانی شد.')
            return redirect('accounts:librarian_list')
    else:
        form = LibrarianForm(instance=librarian)

    return render(request, 'accounts/librarian_form.html', {
        'form': form,
        'action': 'ویرایش کتابدار'
    })


@login_required(login_url='/accounts/login/')
@role_required('admin')
def librarian_delete(request, pk):
    librarian = get_object_or_404(User, pk=pk, role=User.Role.LIBRARIAN)
    if request.method == 'POST':
        librarian.delete()
        messages.success(request, 'کتابدار حذف شد.')
        return redirect('accounts:librarian_list')

    return render(request, 'accounts/librarian_confirm_delete.html', {
        'librarian': librarian
    })


# ─────────────────────────────────────────
# Member Management (FR02) — admin + librarian
# ─────────────────────────────────────────

@login_required(login_url='/accounts/login/')
@role_required('admin', 'librarian')
def member_list(request):
    members = User.objects.filter(
        role__in=[User.Role.STUDENT, User.Role.PROFESSOR]
    ).order_by('last_name')
    return render(request, 'accounts/member_list.html', {'members': members})


@login_required(login_url='/accounts/login/')
@role_required('admin', 'librarian')
def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کاربر با موفقیت ثبت شد.')
            return redirect('accounts:member_list')
    else:
        form = MemberForm()

    return render(request, 'accounts/member_form.html', {
        'form': form,
        'action': 'ثبت کاربر جدید'
    })


@login_required(login_url='/accounts/login/')
@role_required('admin', 'librarian')
def member_edit(request, pk):
    member = get_object_or_404(
        User, pk=pk, role__in=[User.Role.STUDENT, User.Role.PROFESSOR]
    )
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات کاربر بروزرسانی شد.')
            return redirect('accounts:member_list')
    else:
        form = MemberForm(instance=member)

    return render(request, 'accounts/member_form.html', {
        'form': form,
        'action': 'ویرایش کاربر'
    })


@login_required(login_url='/accounts/login/')
@role_required('admin', 'librarian')
def member_delete(request, pk):
    member = get_object_or_404(
        User, pk=pk, role__in=[User.Role.STUDENT, User.Role.PROFESSOR]
    )
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'کاربر حذف شد.')
        return redirect('accounts:member_list')

    return render(request, 'accounts/member_confirm_delete.html', {
        'member': member
    })
