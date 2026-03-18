from django.contrib import admin
from task_manager.models import Label, Status, Task


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "author", "executor", "created_at")
