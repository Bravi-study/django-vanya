from typing import Any, cast

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import SignUpForm, TaskFilterForm, TaskForm
from .models import Task, TaskQuerySet


def task_queryset() -> TaskQuerySet:
    return cast(TaskQuerySet, Task.objects)


class HomePageView(TemplateView):
    template_name = "tasks/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            visible_tasks = task_queryset().visible_to(self.request.user)
            context["dashboard"] = {
                "total": visible_tasks.count(),
                "in_progress": visible_tasks.filter(status=Task.Status.IN_PROGRESS).count(),
                "done": visible_tasks.filter(status=Task.Status.DONE).count(),
            }

        context["top_tags"] = (
            task_queryset()
            .active()
            .values("tags__name")
            .exclude(tags__name__isnull=True)
            .annotate(total=Count("id"))
            .order_by("-total", "tags__name")[:5]
        )
        return context


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("tasks:list")

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("tasks:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Пользователь создан. Теперь можно работать с задачами.")
        return redirect(self.get_success_url())


class VisibleTaskQuerysetMixin(LoginRequiredMixin):
    request: HttpRequest

    def get_queryset(self):
        return task_queryset().with_related().visible_to(self.request.user)


class OwnedTaskQuerysetMixin(LoginRequiredMixin):
    request: HttpRequest

    def get_queryset(self):
        return task_queryset().with_related().filter(owner=self.request.user)


class TaskListView(VisibleTaskQuerysetMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_filter_form(self):
        if not hasattr(self, "_filter_form"):
            self._filter_form = TaskFilterForm(self.request.GET or None)
        return self._filter_form

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_form = self.get_filter_form()

        if not filter_form.is_valid():
            return queryset.active()

        data = filter_form.cleaned_data

        if not data["include_archived"]:
            queryset = queryset.active()

        if data["q"]:
            # В PostgreSQL полнотекстовый поиск обычно выделяют отдельно, а здесь оставляем понятный icontains.
            queryset = queryset.filter(
                Q(title__icontains=data["q"]) | Q(description__icontains=data["q"])
            )

        if data["status"]:
            queryset = queryset.filter(status=data["status"])

        if data["priority"]:
            queryset = queryset.filter(priority=data["priority"])

        if data["overdue"]:
            queryset = queryset.filter(due_date__lt=timezone.localdate()).exclude(
                status=Task.Status.DONE
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["filter_form"] = self.get_filter_form()
        context["summary"] = {
            "total": queryset.count(),
            "done": queryset.filter(status=Task.Status.DONE).count(),
            "overdue": queryset.filter(due_date__lt=timezone.localdate(), is_archived=False)
            .exclude(status=Task.Status.DONE)
            .count(),
        }
        return context


class TaskDetailView(VisibleTaskQuerysetMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Задача создана.")
        return super().form_valid(form)


class TaskUpdateView(OwnedTaskQuerysetMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Задача обновлена.")
        return super().form_valid(form)


class TaskDeleteView(OwnedTaskQuerysetMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        messages.success(request, "Задача удалена.")
        return super().delete(request, *args, **kwargs)
