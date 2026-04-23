from django.contrib import admin

from .forms import TaskForm
from .models import Tag, Task

admin.site.site_header = "Учебная админка Django"
admin.site.site_title = "Django interview demo"
admin.site.index_title = "Управление задачами"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskForm
    list_display = ("title", "status", "priority", "owner", "assignee", "due_date", "is_archived")
    list_filter = ("status", "priority", "is_archived", "tags")
    search_fields = ("title", "description", "owner__username", "assignee__username")
    autocomplete_fields = ("owner", "assignee")
    filter_horizontal = ("tags",)
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("owner", "assignee")
            .prefetch_related("tags")
        )
