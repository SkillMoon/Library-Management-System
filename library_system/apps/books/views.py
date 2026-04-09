from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.decorators import role_required
from .models import Book, BookCopy
from .forms import BookForm, BookCopyForm

@login_required
def book_list(request):
    books = Book.objects.all().order_by('-id')
    return render(request, 'books/book_list.html', {'books': books})

@role_required('admin', 'librarian')
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('book_list')
    return render(request, 'books/book_form.html', {'form': form, 'title': 'افزودن کتاب'})

@role_required('admin', 'librarian')
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('book_list')
    return render(request, 'books/book_form.html', {'form': form, 'title': 'ویرایش کتاب'})

@role_required('admin', 'librarian')
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    copies = BookCopy.objects.filter(book=book)
    return render(request, 'books/book_detail.html', {'book': book, 'copies': copies})
