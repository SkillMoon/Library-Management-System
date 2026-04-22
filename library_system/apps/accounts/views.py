from multiprocessing.context import AuthenticationError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import LoginForm, LibrarianForm, MemberForm, ProfileForm
from .models import User, ImportLog
from .decorators import role_required
import openpyxl

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
    template = templates.get(role, 'accounts/dashboard.html')
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

            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


# ─────────────────────────────────────────
# Librarian Management (FR01) — only admin
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

@login_required
@role_required('admin', 'librarian')
def import_users(request):

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'فقط فایل xlsx قابل قبول است.')
            return redirect('accounts:import_users')

        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active

        success_count = 0
        fail_count = 0
        errors = []

        for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            username    = str(row[0]).strip() if row[0] else None
            first_name  = str(row[1]).strip() if row[1] else ''
            last_name   = str(row[2]).strip() if row[2] else ''
            email       = str(row[3]).strip() if row[3] else ''
            role        = str(row[4]).strip() if row[4] else 'student'
            national_id = str(row[5]).strip() if row[5] else None
            phone       = str(row[6]).strip() if row[6] else ''

            if not username or not national_id:
                errors.append(f"ردیف {row_num}: username یا national_id خالی است.")
                fail_count += 1
                continue

            valid_roles = ['admin', 'librarian', 'student', 'professor']
            if role not in valid_roles:
                errors.append(f"ردیف {row_num}: role نامعتبر است ({role}).")
                fail_count += 1
                continue

            if User.objects.filter(username=username).exists():
                errors.append(f"ردیف {row_num}: username «{username}» تکراری است.")
                fail_count += 1
                continue

            try:
                user = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    role=role,
                    national_id=national_id,
                    phone=phone,
                )
                user.set_password(national_id)
                user.save()
                success_count += 1
            except Exception as e:
                errors.append(f"ردیف {row_num}: خطا — {str(e)}")
                fail_count += 1

        ImportLog.objects.create(
            imported_by=request.user,
            file_name=excel_file.name,
            total_rows=success_count + fail_count,
            success_count=success_count,
            fail_count=fail_count,
            errors='\n'.join(errors),
        )

        messages.success(request, f"Import انجام شد: {success_count} موفق، {fail_count} ناموفق.")
        return redirect('accounts:import_users')

    return render(request, 'accounts/import_users.html')
