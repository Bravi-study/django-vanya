from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Task

User = get_user_model()


class SignUpForm(UserCreationForm):
    """Показывает, как безопасно расширять стандартные формы Django."""

    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="Имя", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "tags",
            "due_date",
            "is_archived",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = User.objects.order_by("username")
        self.fields["tags"].queryset = self.fields["tags"].queryset.order_by("name")

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Заголовок не может состоять только из пробелов.")
        return title


class TaskFilterForm(forms.Form):
    q = forms.CharField(label="Поиск", max_length=100, required=False)
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[("", "Все статусы"), *Task.Status.choices],
    )
    priority = forms.ChoiceField(
        label="Приоритет",
        required=False,
        choices=[("", "Любой приоритет"), *Task.Priority.choices],
    )
    overdue = forms.BooleanField(label="Только просроченные", required=False)
    include_archived = forms.BooleanField(label="Показывать архив", required=False)
