from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import BorrowRequest, Borrow, Fine
from .forms import BorrowRequestForm, BorrowRequestResponseForm, ReturnForm
from apps.books.models import BookCopy
from apps.accounts.decorators import role_required


FINE_PER_DAY = {
    'student': 5000,    # FR16
    'professor': 2000,  # FR17
}
BORROW_DURATION_DAYS = 14


@login_required
def borrow_request_create(request):
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
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
    requests_list = BorrowRequest.objects.filter(
        user=request.user
    ).select_related('book').order_by('-request_date')
    return render(request, 'borrowing/my_requests.html', {'requests': requests_list})


@login_required
@role_required('admin', 'librarian')
def borrow_request_list(request):
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
    borrow_request = get_object_or_404(
        BorrowRequest, pk=pk, status=BorrowRequest.Status.PENDING
    )

    if request.method == 'POST':
        form = BorrowRequestResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            note = form.cleaned_data['note']

            if note:
                borrow_request.note = note

            if action == 'approved':
                copy = BookCopy.objects.filter(
                    book=borrow_request.book,
                    status='available'
                ).first()

                if not copy:
                    messages.error(request, 'نسخه موجودی یافت نشد. درخواست تأیید نشد.')
                    return redirect('borrowing:borrow_request_list')

                copy.status = 'borrowed'
                copy.save()

                Borrow.objects.create(
                    user=borrow_request.user,
                    book_copy=copy,
                    borrow_request=borrow_request,
                    librarian=request.user,
                    borrow_date=timezone.now().date(),
                    due_date=timezone.now().date() + timedelta(days=BORROW_DURATION_DAYS),
                    status=Borrow.Status.ACTIVE,
                )
                borrow_request.status = BorrowRequest.Status.APPROVED
                borrow_request.save()
                messages.success(request, 'درخواست تأیید و امانت ثبت شد.')

            else:
                borrow_request.status = BorrowRequest.Status.REJECTED
                borrow_request.save()
                messages.info(request, 'درخواست رد شد.')

            return redirect('borrowing:borrow_request_list')
    else:
        form = BorrowRequestResponseForm()

    return render(request, 'borrowing/borrow_request_respond.html', {
        'form': form,
        'borrow_request': borrow_request,
    })


@login_required
@role_required('admin', 'librarian')
def borrow_return(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id, status=Borrow.Status.ACTIVE)
    form = ReturnForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        condition = form.cleaned_data['condition']
        today = timezone.now().date()

        borrow.return_date = today
        borrow.status = Borrow.Status.RETURNED
        borrow.save()

        borrow.book_copy.status = condition  # 'available' یا 'damaged'
        borrow.book_copy.save()

        if today > borrow.due_date:
            days_late = (today - borrow.due_date).days
            rate = FINE_PER_DAY.get(borrow.user.role, 5000)
            amount = days_late * rate

            Fine.objects.create(
                borrow=borrow,
                amount=amount,
                days_late=days_late,
                is_paid=False,
                registered_by=request.user,
            )
            messages.warning(
                request,
                f"کتاب با {days_late} روز تأخیر برگشت داده شد. جریمه: {amount:,} ریال"
            )
        else:
            messages.success(request, 'کتاب با موفقیت برگشت داده شد.')

        return redirect('borrowing:borrow_list')

    return render(request, 'borrowing/borrow_return.html', {
        'form': form,
        'borrow': borrow,
    })


@login_required
@role_required('admin', 'librarian')
def borrow_list(request):
    borrows = Borrow.objects.select_related(
        'user', 'book_copy__book', 'fine'
    ).order_by('-borrow_date')
    return render(request, 'borrowing/borrow_list.html', {'borrows': borrows})


@login_required
def my_borrows(request):
    borrows = Borrow.objects.filter(
        user=request.user
    ).select_related('book_copy__book', 'fine').order_by('-borrow_date')
    return render(request, 'borrowing/my_borrows.html', {'borrows': borrows})

@login_required
@role_required('admin', 'librarian')
def borrow_direct_issue(request):
    """
    کتابدار مستقیماً امانت را برای یک کاربر دیگر ثبت می‌کند.
    بدون نیاز به BorrowRequest.
    """
    from .forms import DirectBorrowForm

    if request.method == 'POST':
        form = DirectBorrowForm(request.POST)
        if form.is_valid():
            target_user = form.cleaned_data['user']
            copy = form.cleaned_data['book_copy']

            # بررسی مجدد وضعیت نسخه (race condition احتمالی)
            if copy.status != 'available':
                messages.error(request, 'این نسخه در حال حاضر موجود نیست.')
                return render(request, 'borrowing/borrow_direct_issue.html', {'form': form})

            # تغییر وضعیت نسخه
            copy.status = 'borrowed'
            copy.save()

            # ثبت امانت مستقیم
            Borrow.objects.create(
                user=target_user,
                book_copy=copy,
                borrow_request=None,       # بدون درخواست آنلاین
                librarian=request.user,    # کتابدار فعلی
                borrow_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=BORROW_DURATION_DAYS),
                status=Borrow.Status.ACTIVE,
            )

            messages.success(
                request,
                f'امانت برای {target_user.get_full_name() or target_user.username} '
                f'با موفقیت ثبت شد.'
            )
            return redirect('borrowing:borrow_list')
    else:
        form = DirectBorrowForm()

    return render(request, 'borrowing/borrow_direct_issue.html', {'form': form})

@login_required
@role_required('admin', 'librarian')
def fine_list(request):
    fines = Fine.objects.select_related(
        'borrow__user', 'borrow__book_copy__book', 'registered_by'
    ).order_by('is_paid', '-created_at')

    f = request.GET.get('filter')
    if f == 'paid':
        fines = fines.filter(is_paid=True)
    elif f == 'unpaid':
        fines = fines.filter(is_paid=False)

    return render(request, 'borrowing/fine_list.html', {'fines': fines})


@login_required
@role_required('admin', 'librarian')
def fine_mark_paid(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id, is_paid=False)
    fine.is_paid = True
    fine.paid_at = timezone.now()
    fine.save()
    messages.success(request, f'جریمه شماره {fine.id} به عنوان پرداخت‌شده ثبت شد.')
    return redirect('borrowing:fine_list')
