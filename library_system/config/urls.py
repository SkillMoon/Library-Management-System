from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('books/', include('apps.books.urls')),
    path('borrowing/', include('apps.borrowing.urls')),
    path('', lambda request: redirect('accounts:login')),
]
