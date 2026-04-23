from django.utils import timezone
from rest_framework import serializers

from .models import Tag, Task


class TaskSerializer(serializers.ModelSerializer):
    tag_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name", source="tags"
    )
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "tags",
            "tag_names",
            "due_date",
            "is_archived",
            "owner_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "owner_username"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Заголовок не может состоять только из пробелов.")
        return value

    def validate(self, attrs):
        due_date = attrs.get("due_date")
        status = attrs.get("status")

        if self.instance:
            due_date = due_date if due_date is not None else self.instance.due_date
            status = status or self.instance.status

        if due_date and due_date < timezone.localdate() and status != Task.Status.DONE:
            raise serializers.ValidationError(
                {"due_date": "Прошедший срок допустим только для задач со статусом 'Готово'."}
            )

        return attrs
