from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Tag(models.Model):
    """Справочная модель для демонстрации M2M-связи с задачами."""

    name = models.CharField("название", max_length=64, unique=True)
    slug = models.SlugField("slug", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class TaskQuerySet(models.QuerySet):
    def visible_to(self, user):
        """Видимыми считаем задачи владельца и задачи, где пользователь назначен исполнителем."""

        if not user.is_authenticated:
            return self.none()
        return self.filter(Q(owner=user) | Q(assignee=user)).distinct()

    def with_related(self):
        """Селектим связи заранее, чтобы list/detail не провоцировали N+1 запросы."""

        return self.select_related("owner", "assignee").prefetch_related("tags")

    def active(self):
        return self.filter(is_archived=False)


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "Нужно сделать"
        IN_PROGRESS = "in_progress", "В работе"
        DONE = "done", "Готово"

    class Priority(models.TextChoices):
        LOW = "low", "Низкий"
        MEDIUM = "medium", "Средний"
        HIGH = "high", "Высокий"

    title = models.CharField("заголовок", max_length=200)
    description = models.TextField("описание", blank=True)
    status = models.CharField("статус", max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(
        "приоритет",
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_tasks",
        verbose_name="владелец",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
        verbose_name="исполнитель",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks", verbose_name="теги")
    due_date = models.DateField("срок", null=True, blank=True)
    is_archived = models.BooleanField("в архиве", default=False)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["is_archived", "due_date", "-updated_at"]
        verbose_name = "задача"
        verbose_name_plural = "задачи"
        indexes = [
            # Такие индексы полезно обсуждать на собеседовании: они отражают реальные фильтры списка.
            models.Index(fields=["owner", "status"], name="task_owner_status_idx"),
            models.Index(fields=["assignee", "due_date"], name="task_assignee_due_idx"),
        ]

    def clean(self):
        super().clean()
        if (
            self.due_date
            and self.due_date < timezone.localdate()
            and self.status != self.Status.DONE
        ):
            raise ValidationError(
                {"due_date": "Прошедший срок допустим только для задач со статусом 'Готово'."}
            )

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.due_date
            and self.due_date < timezone.localdate()
            and self.status != self.Status.DONE
            and not self.is_archived
        )

    def can_be_edited_by(self, user) -> bool:
        return user.is_authenticated and self.owner == user

    def get_absolute_url(self):
        return reverse("tasks:detail", args=[self.pk])

    def __str__(self) -> str:
        return self.title
