import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from projects.models import Project
from users.models import User

DEFAULT_FIXTURE = os.path.join(
    os.path.dirname(__file__), "demo_projects.json"
)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Не удалять старые проекты",
        )
        parser.add_argument(
            "--fixture",
            default=DEFAULT_FIXTURE,
            help="Путь к JSON-файлу с данными проектов",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fixture_path = options["fixture"]

        if not os.path.exists(fixture_path):
            raise CommandError(f"Файл не найден: {fixture_path}")

        with open(fixture_path, encoding="utf-8") as f:
            demo_projects = json.load(f)

        users_by_email = {
            user.email: user
            for user in User.objects.filter(
                email__in=self._all_emails_from_config(demo_projects)
            )
        }

        missing_emails = (
            self._all_emails_from_config(demo_projects) - set(users_by_email.keys())
        )
        if missing_emails:
            raise CommandError(
                "Не найдены пользователи для проектов: "
                + ", ".join(sorted(missing_emails))
            )

        self.stdout.write(self.style.WARNING("Создание проектов"))

        for item in demo_projects:
            owner = users_by_email[item["owner_email"]]

            project, created = Project.objects.get_or_create(
                github_url=item["github_url"],
                defaults={
                    "owner": owner,
                    "name": item["name"],
                    "description": item["description"],
                    "status": item["status"],
                },
            )

            if not created:
                project.owner = owner
                project.name = item["name"]
                project.description = item["description"]
                project.status = item["status"]
                project.save()

            project.participants.clear()
            project.participants.add(owner)

            participant_users = [
                users_by_email[email]
                for email in item["participant_emails"]
                if email != owner.email
            ]
            if participant_users:
                project.participants.add(*participant_users)

        self.stdout.write(self.style.SUCCESS("Проекты успешно созданы."))

    def _all_emails_from_config(self, demo_projects):
        emails = set()
        for item in demo_projects:
            emails.add(item["owner_email"])
            emails.update(item["participant_emails"])
        return emails
