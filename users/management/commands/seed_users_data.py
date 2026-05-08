from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project
from users.models import User

DEMO_USERS = [
    {
        "email": "user1@example.com",
        "password": "testtest123",
        "name": "User 1",
        "surname": "User 1",
        "phone": "+79001000001",
        "github_url": "https://github.com/user1",
        "about": "Test",
    },
    {
        "email": "user2@example.com",
        "password": "testtest123",
        "name": "User 2",
        "surname": "User 2",
        "phone": "+79001000002",
        "github_url": "https://github.com/user2",
        "about": "Test",
    },
    {
        "email": "user3@example.com",
        "password": "testtest123",
        "name": "User 3",
        "surname": "User 3",
        "phone": "+79001000003",
        "github_url": "https://github.com/user3",
        "about": "Test",
    },
]


DEMO_PROJECTS = [
    {
        "owner_email": "user1@example.com",
        "name": "Test 1",
        "description": "Test",
        "github_url": "https://github.com/user1/test1",
        "status": "open",
    },
    {
        "owner_email": "user2@example.com",
        "name": "Test 2",
        "description": "Test",
        "github_url": "https://github.com/user2/test2",
        "status": "open",
    },
    {
        "owner_email": "user3@example.com",
        "name": "Test 3",
        "description": "Test",
        "github_url": "https://github.com/user3/test3",
        "status": "open",
    }
]


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Удаление старых данных"))
        self._cleanup_demo_data()

        self.stdout.write(self.style.WARNING("Создание пользователей"))
        users_by_email = self._create_users()

        self.stdout.write(self.style.WARNING("Создание проектов"))
        projects_by_name = self._create_projects(users_by_email)

        self.stdout.write(self.style.WARNING("Создание участников"))
        self._assign_participants(users_by_email, projects_by_name)

        self.stdout.write(self.style.SUCCESS("Демоданные успешно созданы"))

    def _cleanup_demo_data(self):
        demo_emails = [item["email"] for item in DEMO_USERS]
        Project.objects.filter(owner__email__in=demo_emails).delete()
        User.objects.filter(email__in=demo_emails).delete()

    def _create_users(self):
        result = {}

        for user_data in DEMO_USERS:
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

    def _create_projects(self, users_by_email):
        result = {}

        for project_data in DEMO_PROJECTS:
            owner = users_by_email[project_data["owner_email"]]
            project = Project.objects.create(
                owner=owner,
                name=project_data["name"],
                description=project_data["description"],
                github_url=project_data["github_url"],
                status=project_data["status"],
            )
            project.participants.add(owner)
            result[project.name] = project

        return result

    def _assign_participants(self, users_by_email, projects_by_name):
        projects_by_name["Test 1"].participants.add(
            users_by_email["user2@example.com"],
        )
        projects_by_name["Test 2"].participants.add(
            users_by_email["user1@example.com"],
            users_by_email["user3@example.com"],
        )
        projects_by_name["Test 3"].participants.add(
            users_by_email["user1@example.com"],
        )
