"""
URL configuration for task_manager project.
"""

from django.contrib import admin
from django.urls import path

from task_manager import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.IndexView.as_view(), name="home"),
    path("users/", views.UserListView.as_view(), name="users_list"),
    path("users/create/", views.UserCreateView.as_view(), name="users_create"),
    path("users/<int:pk>/update/", views.UserUpdateView.as_view(), name="users_update"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="users_delete"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]
