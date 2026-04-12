from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    path('requests/', views.borrow_request_list, name='borrow_request_list'),
    path('requests/create/', views.borrow_request_create, name='borrow_request_create'),
    path('requests/<int:pk>/respond/', views.borrow_request_respond, name='borrow_request_respond'),
    path('my-requests/', views.my_requests, name='my_requests'),

    path('list/', views.borrow_list, name='borrow_list'),
    path('direct-issue/', views.borrow_direct_issue, name='borrow_direct_issue'),  # ← جدید
    path('return/<int:borrow_id>/', views.borrow_return, name='borrow_return'),
    path('my-borrows/', views.my_borrows, name='my_borrows'),
    path('fines/', views.fine_list, name='fine_list'),
    path('fines/<int:fine_id>/mark-paid/', views.fine_mark_paid, name='fine_mark_paid'),
]
