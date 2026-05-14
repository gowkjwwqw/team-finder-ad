from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models

from .managers import UserManager
from .utils import generate_avatar
from .constants import (
    DEFAULT_AVATAR_FILENAME_TEMPLATE,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
)


class User(AbstractUser):
    username = None

    name = models.CharField(
        "имя",
        max_length=USER_NAME_MAX_LENGTH,
    )
    surname = models.CharField(
        "фамилия",
        max_length=USER_NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        "аватар",
        upload_to="avatars/",
        blank=True,
    )
    phone = models.CharField(
        "телефон",
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
    )
    github_url = models.URLField(
        "GitHub",
        blank=True,
    )
    about = models.TextField(
        "описание",
        blank=True,
        max_length=USER_ABOUT_MAX_LENGTH,
    )
    email = models.EmailField(
        "email",
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(
                DEFAULT_AVATAR_FILENAME_TEMPLATE.format(email=self.email),
                ContentFile(generate_avatar(self.name)),
                save=False,
            )
        super().save(*args, **kwargs)
