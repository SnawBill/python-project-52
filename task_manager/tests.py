from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HomePageTest(TestCase):
    def test_home_page_contains_required_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Менеджер задач")
        self.assertContains(response, "Пользователи")
        self.assertContains(response, "Вход")
        self.assertContains(response, "Регистрация")


class UserFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mike",
            password="StrongPass123",
            first_name="Mike",
            last_name="Smith",
        )
        self.other_user = User.objects.create_user(
            username="john",
            password="StrongPass123",
            first_name="John",
            last_name="Doe",
        )

    def test_users_list_available_without_auth(self):
        response = self.client.get(reverse("users_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "mike")
        self.assertContains(response, "john")

    def test_create_user_redirects_to_login(self):
        response = self.client.post(
            reverse("users_create"),
            {
                "first_name": "Alice",
                "last_name": "Cooper",
                "username": "alice",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("login"))
        self.assertContains(response, "Пользователь успешно зарегистрирован")
        self.assertTrue(User.objects.filter(username="alice").exists())

    def test_login_redirects_to_home(self):
        response = self.client.post(
            reverse("login"),
            {"username": "mike", "password": "StrongPass123"},
            follow=True,
        )

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Вы залогинены")

    def test_logout_works(self):
        self.client.login(username="mike", password="StrongPass123")

        response = self.client.post(reverse("logout"), follow=True)

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Вы разлогинены")

    def test_update_user_redirects_to_users_list(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("users_update", kwargs={"pk": self.user.pk}),
            {
                "first_name": "Michael",
                "last_name": "Smith",
                "username": "mike",
                "password1": "NewStrongPass123",
                "password2": "NewStrongPass123",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("users_list"))
        self.assertContains(response, "Пользователь успешно изменен")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Michael")

    def test_cannot_update_another_user(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("users_update", kwargs={"pk": self.other_user.pk}),
            {
                "first_name": "Hacked",
                "last_name": "User",
                "username": "john",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("users_list"))
        self.assertContains(response, "У вас нет прав для изменения")
        self.other_user.refresh_from_db()
        self.assertEqual(self.other_user.first_name, "John")

    def test_delete_user(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("users_delete", kwargs={"pk": self.user.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("users_list"))
        self.assertContains(response, "Пользователь успешно удален")
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
