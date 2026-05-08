from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from projects.models import Project
from users.models import User

DEMO_PROJECTS = [
    {
        "owner_email": "user1@example.com",
        "name": "Test 1",
        "description": "Test",
        "github_url": "https://github.com/user1/test1",
        "status": "open",
        "participant_emails": [
            "user2@example.com",
        ],
    },
    {
        "owner_email": "user2@example.com",
        "name": "Test 2",
        "description": "Test",
        "github_url": "https://github.com/user2/test2",
        "status": "open",
        "participant_emails": [
            "user1@example.com",
        ],
    },
    {
        "owner_email": "user3@example.com",
        "name": "Test 3",
        "description": "Test",
        "github_url": "https://github.com/user3/test3",
        "status": "open",
        "participant_emails": [
            "user1@example.com",
        ],
    }
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--keep",
            action="store_true",
            help="Не удалять старые проекты",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        users_by_email = {
            user.email: user
            for user in User.objects.filter(
                email__in=self._all_emails_from_config()
            )
        }

        missing_emails = self._all_emails_from_config() - set(users_by_email.keys())
        if missing_emails:
            raise CommandError(
                "Не найдены пользователи для проектов: "
                + ", ".join(sorted(missing_emails))
            )

        self.stdout.write(self.style.WARNING("Создание проектов"))

        for item in DEMO_PROJECTS:
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

    def _all_emails_from_config(self):
        emails = set()

        for item in DEMO_PROJECTS:
            emails.add(item["owner_email"])
            emails.update(item["participant_emails"])

        return emails
