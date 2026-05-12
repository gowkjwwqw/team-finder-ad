from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "name",
        "surname",
        "is_staff",
        "is_active",
        "date_joined",
        "projects_count",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = (
        "email",
        "name",
        "surname",
    )
    ordering = (
        "-date_joined",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),
        (
            "Личная информация",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "about",
                    "phone",
                    "github_url",
                )
            },
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Важные даты",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "email",
                    "name",
                    "surname",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    @admin.display(description="Проектов")
    def projects_count(self, obj):
        return obj.projects_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(projects_count=Count("participated_projects", distinct=True))
