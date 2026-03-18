from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from task_manager.forms import UserCreateForm, UserLoginForm, UserUpdateForm


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
        messages.success(self.request, "Пользователь успешно удален")
        return super().form_valid(form)


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
