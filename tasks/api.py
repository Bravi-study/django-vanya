from rest_framework import generics, permissions

from .models import Task
from .serializers import TaskSerializer


class IsTaskOwnerOrReadOnly(permissions.BasePermission):
    """Исполнитель может читать задачу, но менять её должен владелец."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id


class TaskListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.with_related().visible_to(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskOwnerOrReadOnly]

    def get_queryset(self):
        return Task.objects.with_related().visible_to(self.request.user)
