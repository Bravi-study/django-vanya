from django.urls import path

from .api import TaskListCreateAPIView, TaskRetrieveUpdateDestroyAPIView
from .views import (
    HomePageView,
    SignUpView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

app_name = "tasks"


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("tasks/", TaskListView.as_view(), name="list"),
    path("tasks/create/", TaskCreateView.as_view(), name="create"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="detail"),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="delete"),
    path("api/tasks/", TaskListCreateAPIView.as_view(), name="api-list"),
    path("api/tasks/<int:pk>/", TaskRetrieveUpdateDestroyAPIView.as_view(), name="api-detail"),
]
