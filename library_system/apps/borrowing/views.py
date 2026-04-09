from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import BorrowRequest, Borrow
from .forms import BorrowRequestForm, BorrowRequestResponseForm
from apps.books.models import BookCopy
from apps.accounts.decorators import role_required


@login_required
def borrow_request_create(request):
    """دانشجو/استاد درخواست امانت ثبت می‌کنه"""
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            # بررسی نسخه موجود قبل از ثبت درخواست
            book = form.cleaned_data['book']
            if not book.available_copies:
                messages.error(request, 'نسخه موجودی برای این کتاب وجود ندارد.')
                return render(request, 'borrowing/borrow_request_form.html', {'form': form})

            borrow_request = form.save(commit=False)
            borrow_request.user = request.user
            borrow_request.save()
            messages.success(request, 'درخواست امانت با موفقیت ثبت شد.')
            return redirect('borrowing:my_requests')
    else:
        form = BorrowRequestForm()
    return render(request, 'borrowing/borrow_request_form.html', {'form': form})


@login_required
def my_requests(request):
    """لیست درخواست‌های خود کاربر"""
    requests_list = BorrowRequest.objects.filter(
        user=request.user
    ).select_related('book').order_by('-request_date')
    return render(request, 'borrowing/my_requests.html', {'requests': requests_list})


@login_required
@role_required('admin', 'librarian')
def borrow_request_list(request):
    """لیست همه درخواست‌ها برای کتابدار/ادمین"""
    status_filter = request.GET.get('status', 'pending')
    requests_list = BorrowRequest.objects.filter(
        status=status_filter
    ).select_related('user', 'book').order_by('-request_date')
    return render(request, 'borrowing/borrow_request_list.html', {
        'requests': requests_list,
        'status_filter': status_filter,
    })


@login_required
@role_required('admin', 'librarian')
def borrow_request_respond(request, pk):
    """کتابدار درخواست را تأیید یا رد می‌کند"""
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, status=BorrowRequest.Status.PENDING)

    if request.method == 'POST':
        form = BorrowRequestResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            note = form.cleaned_data['note']

            borrow_request.status = action
            borrow_request.response_date = timezone.now()
            if note:
                borrow_request.note = note
            borrow_request.save()

            if action == 'approved':
                # اختصاص اولین نسخه موجود
                copy = BookCopy.objects.filter(
                    book=borrow_request.book,
                    is_available=True
                ).first()

                if not copy:
                    messages.error(request, 'نسخه موجودی یافت نشد. درخواست تأیید نشد.')
                    borrow_request.status = BorrowRequest.Status.PENDING
                    borrow_request.save()
                    return redirect('borrowing:borrow_request_list')

                copy.is_available = False
                copy.save()

                Borrow.objects.create(
                    user=borrow_request.user,
                    book_copy=copy,
                    borrow_request=borrow_request,
                    due_date=timezone.now().date() + timedelta(days=14),
                )
                messages.success(request, 'درخواست تأیید و امانت ثبت شد.')
            else:
                messages.info(request, 'درخواست رد شد.')

            return redirect('borrowing:borrow_request_list')
    else:
        form = BorrowRequestResponseForm()

    return render(request, 'borrowing/borrow_request_respond.html', {
        'form': form,
        'borrow_request': borrow_request,
    })
