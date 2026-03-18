from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task_manager.models import Label, Status, Task


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].label = _("Имя")
        self.fields["last_name"].label = _("Фамилия")
        self.fields["username"].label = _("Имя пользователя")
        self.fields["password1"].label = _("Пароль")
        self.fields["password2"].label = _("Подтверждение пароля")


class UserUpdateForm(UserCreateForm):
    def clean_username(self):
        username = self.cleaned_data["username"]
        queryset = User.objects.filter(username__iexact=username).exclude(
            pk=self.instance.pk
        )
        if queryset.exists():
            raise ValidationError(_("A user with that username already exists."))
        return username


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Имя пользователя"))
    password = forms.CharField(label=_("Пароль"), widget=forms.PasswordInput)


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = _("Имя")


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "description", "status", "executor", "labels")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = _("Имя")
        self.fields["description"].label = _("Описание")
        self.fields["status"].label = _("Статус")
        self.fields["executor"].label = _("Исполнитель")
        self.fields["labels"].label = _("Метки")
        self.fields["executor"].label_from_instance = (
            lambda user: user.get_full_name().strip() or user.username
        )


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].label = _("Имя")
