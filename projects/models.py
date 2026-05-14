from django.conf import settings
from django.db import models
from django.urls import reverse

from .constants import (
    PROJECT_NAME_LENGTH,
    PROJECT_STATUS_LENGTH,
    SKILL_MAX_LENGTH,
)


class ProjectStatus(models.TextChoices):
    OPEN = "open", "Открыт"
    CLOSED = "closed", "Закрыт"


class Skill(models.Model):
    name = models.CharField("название", max_length=SKILL_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name_plural = "Навыки"
        verbose_name = "Навык"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="автор",
    )
    name = models.CharField(
        "название",
        max_length=PROJECT_NAME_LENGTH,
    )
    description = models.TextField(
        "описание",
        blank=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    status = models.CharField(
        "статус",
        max_length=PROJECT_STATUS_LENGTH,
        choices=ProjectStatus.choices,
        default=ProjectStatus.OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name="участники",
    )
    created_at = models.DateTimeField(
        "дата публикации",
        auto_now_add=True,
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="projects",
        blank=True,
        verbose_name="навыки",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})
