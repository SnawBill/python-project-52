from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Label, Status, Task


class HomePageTest(TestCase):
    def test_home_page_contains_required_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Менеджер задач")
        self.assertContains(response, "Пользователи")
        self.assertContains(response, "Статусы")
        self.assertContains(response, "Задачи")
        self.assertContains(response, "Метки")
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

    def test_cannot_delete_user_linked_to_task(self):
        status = Status.objects.create(name="new")
        Task.objects.create(
            name="task-for-user",
            description="",
            status=status,
            author=self.user,
            executor=self.user,
        )
        self.client.login(username="mike", password="StrongPass123")

        response = self.client.post(
            reverse("users_delete", kwargs={"pk": self.user.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("users_list"))
        self.assertContains(response, "Невозможно удалить пользователя")
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())


class StatusFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mike",
            password="StrongPass123",
        )
        self.status = Status.objects.create(name="новый")

    def test_statuses_list_requires_auth(self):
        response = self.client.get(reverse("statuses_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('statuses_list')}")

    def test_statuses_list_for_authorized_user(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.get(reverse("statuses_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "новый")

    def test_create_status(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("statuses_create"),
            {"name": "в работе"},
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses_list"))
        self.assertContains(response, "Статус успешно создан")
        self.assertTrue(Status.objects.filter(name="в работе").exists())

    def test_update_status(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("statuses_update", kwargs={"pk": self.status.pk}),
            {"name": "на тестировании"},
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses_list"))
        self.assertContains(response, "Статус успешно изменен")
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "на тестировании")

    def test_delete_status(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("statuses_delete", kwargs={"pk": self.status.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("statuses_list"))
        self.assertContains(response, "Статус успешно удален")
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())

    def test_status_unique_validation(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("statuses_create"),
            {"name": "новый"},
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertTrue(
            "уже существует" in content or "already exists" in content
        )


class TaskFlowTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author",
            password="StrongPass123",
        )
        self.executor = User.objects.create_user(
            username="executor",
            password="StrongPass123",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="StrongPass123",
        )
        self.status = Status.objects.create(name="в работе")
        self.label = Label.objects.create(name="bug")
        self.task = Task.objects.create(
            name="Task One",
            description="First task",
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        self.task.labels.add(self.label)

    def test_tasks_list_requires_auth(self):
        response = self.client.get(reverse("tasks_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tasks_list')}")

    def test_tasks_list_for_authorized_user(self):
        self.client.login(username="author", password="StrongPass123")
        response = self.client.get(reverse("tasks_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task One")

    def test_create_task(self):
        self.client.login(username="author", password="StrongPass123")
        response = self.client.post(
            reverse("tasks_create"),
            {
                "name": "Task Two",
                "description": "Created from test",
                "status": self.status.pk,
                "executor": self.executor.pk,
                "labels": [self.label.pk],
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks_list"))
        self.assertContains(response, "Задача успешно создана")
        created_task = Task.objects.get(name="Task Two")
        self.assertEqual(created_task.author, self.author)
        self.assertEqual(created_task.executor, self.executor)
        self.assertEqual(created_task.status, self.status)

    def test_task_detail_requires_auth(self):
        response = self.client.get(reverse("tasks_detail", kwargs={"pk": self.task.pk}))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('tasks_detail', kwargs={'pk': self.task.pk})}",
        )

    def test_update_task(self):
        self.client.login(username="author", password="StrongPass123")
        response = self.client.post(
            reverse("tasks_update", kwargs={"pk": self.task.pk}),
            {
                "name": "Task One Updated",
                "description": "Updated description",
                "status": self.status.pk,
                "executor": self.executor.pk,
                "labels": [self.label.pk],
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks_list"))
        self.assertContains(response, "Задача успешно изменена")
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Task One Updated")

    def test_only_author_can_delete_task(self):
        self.client.login(username="other", password="StrongPass123")
        response = self.client.post(
            reverse("tasks_delete", kwargs={"pk": self.task.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks_list"))
        self.assertContains(response, "Задачу может удалить только ее автор")
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_author_can_delete_task(self):
        self.client.login(username="author", password="StrongPass123")
        response = self.client.post(
            reverse("tasks_delete", kwargs={"pk": self.task.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("tasks_list"))
        self.assertContains(response, "Задача успешно удалена")
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_task_unique_validation(self):
        self.client.login(username="author", password="StrongPass123")
        response = self.client.post(
            reverse("tasks_create"),
            {
                "name": "Task One",
                "description": "Duplicate name",
                "status": self.status.pk,
                "executor": self.executor.pk,
                "labels": [self.label.pk],
            },
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertTrue("уже существует" in content or "already exists" in content)


class LabelFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mike",
            password="StrongPass123",
        )
        self.status = Status.objects.create(name="new")
        self.label = Label.objects.create(name="bug")
        self.task = Task.objects.create(
            name="Task for label",
            description="",
            status=self.status,
            author=self.user,
            executor=self.user,
        )
        self.task.labels.add(self.label)

    def test_labels_list_requires_auth(self):
        response = self.client.get(reverse("labels_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('labels_list')}")

    def test_create_label(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("labels_create"),
            {"name": "feature"},
            follow=True,
        )

        self.assertRedirects(response, reverse("labels_list"))
        self.assertContains(response, "Метка успешно создана")
        self.assertTrue(Label.objects.filter(name="feature").exists())

    def test_update_label(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("labels_update", kwargs={"pk": self.label.pk}),
            {"name": "bugfix"},
            follow=True,
        )

        self.assertRedirects(response, reverse("labels_list"))
        self.assertContains(response, "Метка успешно изменена")
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "bugfix")

    def test_cannot_delete_linked_label(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("labels_delete", kwargs={"pk": self.label.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("labels_list"))
        self.assertContains(response, "Невозможно удалить метку")
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())

    def test_delete_unlinked_label(self):
        self.client.login(username="mike", password="StrongPass123")
        free_label = Label.objects.create(name="free")
        response = self.client.post(
            reverse("labels_delete", kwargs={"pk": free_label.pk}),
            follow=True,
        )

        self.assertRedirects(response, reverse("labels_list"))
        self.assertContains(response, "Метка успешно удалена")
        self.assertFalse(Label.objects.filter(pk=free_label.pk).exists())

    def test_label_unique_validation(self):
        self.client.login(username="mike", password="StrongPass123")
        response = self.client.post(
            reverse("labels_create"),
            {"name": "bug"},
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertTrue("уже существует" in content or "already exists" in content)
