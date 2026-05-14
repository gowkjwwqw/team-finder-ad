from .models import Project


def get_project_queryset():
    return (
        Project.objects
        .select_related("owner")
        .prefetch_related("participants", "skills")
    )
