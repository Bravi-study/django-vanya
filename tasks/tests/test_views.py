from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tasks.models import Task

User = get_user_model()


class TaskViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.assignee = User.objects.create_user(username="assignee", password="pass12345")
        self.outsider = User.objects.create_user(username="outsider", password="pass12345")
        self.owned_task = Task.objects.create(title="Моя задача", owner=self.owner)
        self.assigned_task = Task.objects.create(
            title="Назначенная задача",
            owner=self.outsider,
            assignee=self.owner,
        )
        self.hidden_task = Task.objects.create(title="Скрытая задача", owner=self.outsider)

    def test_list_requires_login(self):
        response = self.client.get(reverse("tasks:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_list_shows_only_visible_tasks(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("tasks:list"))
        tasks = list(response.context["tasks"])

        self.assertIn(self.owned_task, tasks)
        self.assertIn(self.assigned_task, tasks)
        self.assertNotIn(self.hidden_task, tasks)

    def test_create_sets_owner_to_logged_in_user(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("tasks:create"),
            data={
                "title": "Новая задача",
                "description": "Описание",
                "status": Task.Status.TODO,
                "priority": Task.Priority.HIGH,
                "assignee": self.assignee.pk,
                "tags": [],
                "due_date": "",
                "is_archived": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title="Новая задача")
        self.assertEqual(task.owner, self.owner)

    def test_task_card_renders_values_instead_of_template_fragments(self):
        self.client.force_login(self.owner)

        list_response = self.client.get(reverse("tasks:list"))
        detail_response = self.client.get(reverse("tasks:detail", args=[self.owned_task.pk]))

        self.assertContains(list_response, "Нужно сделать")
        self.assertContains(list_response, "Средний")
        self.assertContains(list_response, "Исполнитель: не назначен")
        self.assertContains(list_response, "Срок: не указан")

        self.assertContains(detail_response, "Нужно сделать")
        self.assertContains(detail_response, "Средний")
        self.assertContains(detail_response, "Исполнитель")
        self.assertContains(detail_response, "не назначен")
        self.assertContains(detail_response, "не указан")

        for response in (list_response, detail_response):
            self.assertNotContains(response, "{{ task.get_status_display }}")
            self.assertNotContains(response, '{{ task.assignee.username|default:"не назначен" }}')

    def test_non_owner_cannot_edit_task(self):
        self.client.force_login(self.assignee)

        response = self.client.get(reverse("tasks:update", args=[self.owned_task.pk]))

        self.assertEqual(response.status_code, 404)
