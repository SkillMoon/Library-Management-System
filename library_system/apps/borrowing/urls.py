from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    path('request/new/', views.borrow_request_create, name='borrow_request_create'),
    path('request/my/', views.my_requests, name='my_requests'),
    path('request/all/', views.borrow_request_list, name='borrow_request_list'),
    path('request/<int:pk>/respond/', views.borrow_request_respond, name='borrow_request_respond'),
]
