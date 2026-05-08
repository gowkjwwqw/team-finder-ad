from django.urls import path

from .views import (
    ProjectCreateView,
    ProjectDetailView,
    ProjectListView,
    ProjectUpdateView,
    complete_project,
    toggle_participate,
    skill_search,
    skill_add,
    skill_remove,
)

app_name = "projects"

urlpatterns = [
    path("list/", ProjectListView.as_view(), name="list"),
    path("create-project/", ProjectCreateView.as_view(), name="create-project"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ProjectUpdateView.as_view(), name="edit"),
    path("<int:pk>/complete/", complete_project, name="complete"),
    path("<int:pk>/toggle-participate/", toggle_participate, name="toggle-participate"),
    path("skills/", skill_search, name="skill-search"),
    path("<int:pk>/skills/add/", skill_add, name="skill-add"),
    path("<int:pk>/skills/<int:skill_id>/remove/", skill_remove, name="skill-remove"),
]
