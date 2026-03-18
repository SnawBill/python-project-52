from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from task_manager.forms import (
    StatusForm,
    TaskForm,
    UserCreateForm,
    UserLoginForm,
    UserUpdateForm,
)
from task_manager.models import Status, Task


class IndexView(TemplateView):
    template_name = "index.html"


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    ordering = ("id",)


class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        context["button_text"] = "Зарегистрировать"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно зарегистрирован")
        return super().form_valid(form)


class UserPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.pk == self.get_object().pk

    def handle_no_permission(self):
        messages.error(self.request, "У вас нет прав для изменения")
        return redirect("users_list")


class UserUpdateView(LoginRequiredMixin, UserPermissionMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение пользователя"
        context["button_text"] = "Изменить"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Пользователь успешно изменен")
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, UserPermissionMixin, DeleteView):
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Пользователь успешно удален")
            return response
        except ProtectedError:
            messages.error(self.request, "Невозможно удалить пользователя")
            return redirect("users_list")


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse_lazy("home")

    def form_valid(self, form):
        messages.success(self.request, "Вы залогинены")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("home")

    def post(self, request, *args, **kwargs):
        messages.success(self.request, "Вы разлогинены")
        return super().post(request, *args, **kwargs)


class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = "statuses/status_list.html"
    context_object_name = "statuses"
    ordering = ("id",)


class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать статус"
        context["button_text"] = "Создать"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно создан")
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = "statuses/status_form.html"
    success_url = reverse_lazy("statuses_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение статуса"
        context["button_text"] = "Изменить"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Статус успешно изменен")
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = "statuses/status_confirm_delete.html"
    success_url = reverse_lazy("statuses_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Статус успешно удален")
            return response
        except ProtectedError:
            messages.error(self.request, "Невозможно удалить статус")
            return redirect("statuses_list")


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    ordering = ("id",)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создать задачу"
        context["button_text"] = "Создать"
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Задача успешно создана")
        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_url = reverse_lazy("tasks_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение задачи"
        context["button_text"] = "Изменить"
        return context

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно изменена")
        return super().form_valid(form)


class TaskDeletePermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.get_object().author_id == self.request.user.id

    def handle_no_permission(self):
        messages.error(self.request, "Задачу может удалить только ее автор")
        return redirect("tasks_list")


class TaskDeleteView(LoginRequiredMixin, TaskDeletePermissionMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        messages.success(self.request, "Задача успешно удалена")
        return super().form_valid(form)
