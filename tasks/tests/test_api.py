from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from tasks.models import Tag, Task

User = get_user_model()


class TaskApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.assignee = User.objects.create_user(username="assignee", password="pass12345")
        self.outsider = User.objects.create_user(username="outsider", password="pass12345")
        self.tag = Tag.objects.create(name="backend", slug="backend")
        self.owned_task = Task.objects.create(title="API моя", owner=self.owner)
        self.assigned_task = Task.objects.create(
            title="API назначенная", owner=self.outsider, assignee=self.owner
        )
        self.hidden_task = Task.objects.create(title="API скрытая", owner=self.outsider)

    def test_authentication_required_for_task_list(self):
        response = self.client.get(reverse("tasks:api-list"))

        self.assertIn(
            response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}
        )

    def test_list_returns_only_visible_tasks(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(reverse("tasks:api-list"))
        payload = response.json()
        ids = [item["id"] for item in payload]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(ids, [self.owned_task.id, self.assigned_task.id])
        self.assertNotIn(self.hidden_task.id, ids)

    def test_create_sets_owner_automatically(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            reverse("tasks:api-list"),
            data={
                "title": "Новая API задача",
                "description": "Через serializer",
                "status": Task.Status.TODO,
                "priority": Task.Priority.MEDIUM,
                "assignee": self.assignee.pk,
                "tags": [self.tag.pk],
                "is_archived": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(title="Новая API задача")
        self.assertEqual(task.owner, self.owner)
        self.assertEqual(list(task.tags.values_list("id", flat=True)), [self.tag.id])

    def test_non_owner_cannot_update_task(self):
        self.client.force_authenticate(user=self.assignee)

        response = self.client.patch(
            reverse("tasks:api-detail", args=[self.owned_task.pk]),
            data={"title": "Попытка изменить"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
