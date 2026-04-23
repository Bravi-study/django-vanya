from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from tasks.models import Task

User = get_user_model()


class TaskModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")
        self.teammate = User.objects.create_user(username="teammate", password="pass12345")
        self.outsider = User.objects.create_user(username="outsider", password="pass12345")

    def test_visible_to_returns_owned_and_assigned_tasks(self):
        owned = Task.objects.create(title="Моя", owner=self.owner)
        assigned = Task.objects.create(
            title="Назначенная", owner=self.outsider, assignee=self.owner
        )
        hidden = Task.objects.create(title="Чужая", owner=self.outsider)

        visible_ids = list(Task.objects.visible_to(self.owner).values_list("id", flat=True))

        self.assertCountEqual(visible_ids, [owned.id, assigned.id])
        self.assertNotIn(hidden.id, visible_ids)

    def test_full_clean_rejects_past_due_date_for_open_task(self):
        task = Task(
            title="Просроченная",
            owner=self.owner,
            status=Task.Status.TODO,
            due_date=timezone.localdate() - timedelta(days=1),
        )

        with self.assertRaisesMessage(Exception, "Прошедший срок допустим"):
            task.full_clean()

    def test_is_overdue_false_for_done_task(self):
        task = Task.objects.create(
            title="Готовая",
            owner=self.owner,
            status=Task.Status.DONE,
            due_date=timezone.localdate() - timedelta(days=1),
        )

        self.assertFalse(task.is_overdue)
