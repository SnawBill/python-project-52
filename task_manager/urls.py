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
    path(
        "users/<int:pk>/update/",
        views.UserUpdateView.as_view(),
        name="users_update",
    ),
    path(
        "users/<int:pk>/delete/",
        views.UserDeleteView.as_view(),
        name="users_delete",
    ),
    path("statuses/", views.StatusListView.as_view(), name="statuses_list"),
    path(
        "statuses/create/",
        views.StatusCreateView.as_view(),
        name="statuses_create",
    ),
    path(
        "statuses/<int:pk>/update/",
        views.StatusUpdateView.as_view(),
        name="statuses_update",
    ),
    path(
        "statuses/<int:pk>/delete/",
        views.StatusDeleteView.as_view(),
        name="statuses_delete",
    ),
    path("labels/", views.LabelListView.as_view(), name="labels_list"),
    path("labels/create/", views.LabelCreateView.as_view(), name="labels_create"),
    path(
        "labels/<int:pk>/update/",
        views.LabelUpdateView.as_view(),
        name="labels_update",
    ),
    path(
        "labels/<int:pk>/delete/",
        views.LabelDeleteView.as_view(),
        name="labels_delete",
    ),
    path("tasks/", views.TaskListView.as_view(), name="tasks_list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="tasks_create"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="tasks_detail"),
    path(
        "tasks/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="tasks_update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="tasks_delete",
    ),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
]
