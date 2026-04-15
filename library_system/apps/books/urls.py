# apps/books/urls.py

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # ─── Book CRUD ───────────────────────────────────────────
    path('', views.book_list, name='book_list'),
    path('new/', views.book_create, name='book_create'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),

    # path('', views.BookListView.as_view(), name='book_list'),
    # path('new/', views.BookCreateView.as_view(), name='book_create'),
    # path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    # path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    # ─── BookCopy CRUD (nested under book) ───────────────────
    path('<int:book_pk>/copies/', views.copy_list, name='copy_list'),
    path('<int:book_pk>/copies/create/', views.copy_create, name='copy_create'),
    path('copies/<int:pk>/edit/', views.copy_edit, name='copy_edit'),
    path('copies/<int:pk>/delete/', views.copy_delete, name='copy_delete'),

]
