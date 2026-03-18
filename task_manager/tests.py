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
