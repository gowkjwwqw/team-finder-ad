from django.contrib import admin

from .models import Project, Skill


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "status",
        "created_at",
        "participants_count",
        "skills_list",
    )
    list_filter = (
        "status",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "owner__email",
        "owner__name",
        "owner__surname",
    )
    filter_horizontal = (
        "participants",
    )

    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = "Участники"

    def skills_list(self, obj):
        return ", ".join(obj.skills.values_list("name", flat=True))
    skills_list.short_description = "Скиллы"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
