from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Profile (FR04)
    path('profile/', views.profile_view, name='profile'),

    # Librarian Management (FR01) — admin only
    path('librarians/',                    views.librarian_list,   name='librarian_list'),
    path('librarians/create/',             views.librarian_create, name='librarian_create'),
    path('librarians/<int:pk>/edit/',      views.librarian_edit,   name='librarian_edit'),
    path('librarians/<int:pk>/delete/',    views.librarian_delete, name='librarian_delete'),

    # Member Management (FR02) — admin + librarian
    path('members/',                       views.member_list,   name='member_list'),
    path('members/create/',                views.member_create, name='member_create'),
    path('members/<int:pk>/edit/',         views.member_edit,   name='member_edit'),
    path('members/<int:pk>/delete/',       views.member_delete, name='member_delete'),
]
