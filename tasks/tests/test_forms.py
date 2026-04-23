from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from tasks.forms import TaskForm
from tasks.models import Task

User = get_user_model()


class TaskFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass12345")

    def test_title_is_stripped(self):
        form = TaskForm(
            data={
                "title": "  Нормализованная задача  ",
                "description": "",
                "status": Task.Status.TODO,
                "priority": Task.Priority.MEDIUM,
                "assignee": "",
                "tags": [],
                "due_date": "",
                "is_archived": "",
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Нормализованная задача")

    def test_past_due_date_is_invalid_for_open_task(self):
        form = TaskForm(
            data={
                "title": "Задача",
                "description": "",
                "status": Task.Status.TODO,
                "priority": Task.Priority.MEDIUM,
                "assignee": "",
                "tags": [],
                "due_date": (timezone.localdate() - timedelta(days=1)).isoformat(),
                "is_archived": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)
