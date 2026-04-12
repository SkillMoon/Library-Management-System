# apps/books/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from apps.accounts.decorators import role_required
from .models import Book, BookCopy
from .forms import BookForm, BookCopyForm


# ─────────────────────────────────────────
#  Book CRUD
# ─────────────────────────────────────────

@login_required
def book_list(request):
    books = Book.objects.prefetch_related('copies').all().order_by('-id')

    # ─── فیلترهای جستجوی پیشرفته (FR08) ───
    title     = request.GET.get('title', '').strip()
    author    = request.GET.get('author', '').strip()
    publisher = request.GET.get('publisher', '').strip()
    category  = request.GET.get('category', '').strip()
    isbn      = request.GET.get('isbn', '').strip()

    if title:
        books = books.filter(title__icontains=title)
    if author:
        books = books.filter(author__icontains=author)
    if publisher:
        books = books.filter(publisher__icontains=publisher)
    if category:
        books = books.filter(category__icontains=category)
    if isbn:
        books = books.filter(isbn__icontains=isbn)

    return render(request, 'books/book_list.html', {
        'books': books,
        'search': {
            'title': title,
            'author': author,
            'publisher': publisher,
            'category': category,
            'isbn': isbn,
        }
    })

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copies = book.copies.all()
    return render(request, 'books/book_detail.html', {
        'book': book,
        'copies': copies
    })


@role_required('admin', 'librarian')
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        # ✅ اگر total_copies > 0 بود، نسخه‌ها رو auto-generate کن
        total = book.total_copies or 0
        for i in range(1, total + 1):
            # فرمت کد: ISBN-001, ISBN-002, ...
            BookCopy.objects.create(
                book=book,
                copy_code=f"{book.isbn}-{str(i).zfill(3)}",
                status='available'
            )
        messages.success(request, f'کتاب "{book.title}" با {total} نسخه اضافه شد.')
        return redirect('books:book_list')
    return render(request, 'books/book_form.html', {
        'form': form,
        'title': 'افزودن کتاب'
    })


@role_required('admin', 'librarian')
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    old_total = book.total_copies
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        book = form.save()
        new_total = book.total_copies
        # ✅ اگر تعداد نسخه‌ها افزایش پیدا کرد، نسخه‌های جدید بساز
        if new_total > old_total:
            existing_count = book.copies.count()
            for i in range(existing_count + 1, new_total + 1):
                BookCopy.objects.create(
                    book=book,
                    copy_code=f"{book.isbn}-{str(i).zfill(3)}",
                    status='available'
                )
            messages.success(
                request,
                f'{new_total - old_total} نسخه جدید اضافه شد.'
            )
        messages.success(request, f'کتاب "{book.title}" ویرایش شد.')
        return redirect('books:book_list')
    return render(request, 'books/book_form.html', {
        'form': form,
        'title': 'ویرایش کتاب'
    })


@role_required('admin', 'librarian')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'کتاب "{title}" حذف شد.')
        return redirect('books:book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})


# ─────────────────────────────────────────
#  BookCopy CRUD
# ─────────────────────────────────────────

@role_required('admin', 'librarian')
def copy_list(request, book_pk):
    """لیست نسخه‌های یک کتاب خاص"""
    book = get_object_or_404(Book, pk=book_pk)
    copies = book.copies.all().order_by('copy_code')
    return render(request, 'books/copy_list.html', {
        'book': book,
        'copies': copies,
        'available_count': copies.filter(status='available').count(),
        'borrowed_count': copies.filter(status='borrowed').count(),
    })


@role_required('admin', 'librarian')
def copy_create(request, book_pk):
    """افزودن نسخه جدید به یک کتاب"""
    book = get_object_or_404(Book, pk=book_pk)
    # پیش‌پر کردن فیلد book در فرم
    initial = {'book': book}
    form = BookCopyForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        copy = form.save(commit=False)
        copy.book = book  # مطمئن می‌شیم book درست ست شده
        copy.save()
        # ✅ total_copies رو sync کن
        book.total_copies = book.copies.count()
        book.save(update_fields=['total_copies'])
        messages.success(request, f'نسخه "{copy.copy_code}" اضافه شد.')
        return redirect('books:copy_list', book_pk=book.pk)
    return render(request, 'books/copy_form.html', {
        'form': form,
        'book': book,
        'title': 'افزودن نسخه'
    })


@role_required('admin', 'librarian')
def copy_edit(request, pk):
    """ویرایش یک نسخه"""
    copy = get_object_or_404(BookCopy, pk=pk)
    book = copy.book
    form = BookCopyForm(request.POST or None, instance=copy)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'نسخه "{copy.copy_code}" ویرایش شد.')
        return redirect('books:copy_list', book_pk=book.pk)
    return render(request, 'books/copy_form.html', {
        'form': form,
        'book': book,
        'title': 'ویرایش نسخه'
    })


@role_required('admin', 'librarian')
def copy_delete(request, pk):
    """حذف یک نسخه"""
    copy = get_object_or_404(BookCopy, pk=pk)
    book = copy.book
    if request.method == 'POST':
        code = copy.copy_code
        # ✅ نسخه‌ای که امانت داده شده رو نمی‌شه حذف کرد
        if copy.status == 'borrowed':
            messages.error(request, 'این نسخه در حال امانت است و قابل حذف نیست.')
            return redirect('books:copy_list', book_pk=book.pk)
        copy.delete()
        # ✅ total_copies رو sync کن
        book.total_copies = book.copies.count()
        book.save(update_fields=['total_copies'])
        messages.success(request, f'نسخه "{code}" حذف شد.')
        return redirect('books:copy_list', book_pk=book.pk)
    return render(request, 'books/copy_confirm_delete.html', {
        'copy': copy,
        'book': book
    })
