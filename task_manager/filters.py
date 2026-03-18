import django_filters
from django import forms
from django.contrib.auth.models import User

from task_manager.models import Label, Status, Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label="Статус",
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label="Исполнитель",
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(),
        field_name="labels",
        label="Метка",
    )
    self_tasks = django_filters.BooleanFilter(
        method="filter_self_tasks",
        label="Только свои задачи",
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = Task
        fields = ("status", "executor", "labels", "self_tasks")

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        for name, field in self.form.fields.items():
            if name == "self_tasks":
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-select"})

    def filter_self_tasks(self, queryset, _, value):
        if value and self.request and self.request.user.is_authenticated:
            return queryset.filter(author=self.request.user)
        return queryset
