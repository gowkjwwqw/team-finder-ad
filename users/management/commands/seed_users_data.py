import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project
from users.models import User

DEFAULT_FIXTURE = os.path.join(os.path.dirname(__file__), "demo_data.json")


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=DEFAULT_FIXTURE,
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = options["fixture"]

        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        demo_users = data["users"]
        demo_projects = data["projects"]

        self.stdout.write(self.style.WARNING("Удаление старых данных"))
        self._cleanup_demo_data(demo_users)

        self.stdout.write(self.style.WARNING("Создание пользователей"))
        users_by_email = self._create_users(demo_users)

        self.stdout.write(self.style.WARNING("Создание проектов и участников"))
        self._create_projects(demo_projects, users_by_email)

        self.stdout.write(self.style.SUCCESS("Демоданные успешно созданы"))

    def _cleanup_demo_data(self, demo_users):
        demo_emails = [u["email"] for u in demo_users]
        Project.objects.filter(owner__email__in=demo_emails).delete()
        User.objects.filter(email__in=demo_emails).delete()

    def _create_users(self, demo_users):
        result = {}
        for user_data in demo_users:
            user = User.objects.create_user(
                email=user_data["email"],
                password=user_data["password"],
                name=user_data["name"],
                surname=user_data["surname"],
                phone=user_data["phone"],
                github_url=user_data["github_url"],
                about=user_data["about"],
            )
            result[user.email] = user
        return result

    def _create_projects(self, demo_projects, users_by_email):
        for project_data in demo_projects:
            owner = users_by_email[project_data["owner_email"]]
            project = Project.objects.create(
                owner=owner,
                name=project_data["name"],
                description=project_data["description"],
                github_url=project_data["github_url"],
                status=project_data["status"],
            )
            project.participants.add(owner)

            for email in project_data.get("participants", []):
                project.participants.add(users_by_email[email])
