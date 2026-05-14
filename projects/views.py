import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .mixins import OwnerRequiredMixin
from .utils import get_project_queryset
from .models import Project, ProjectStatus, Skill
from .constants import (
    PAGINATE_BY,
    ERROR_STATUS,
    OK_STATUS,
    METHOD_NOT_ALLOWED_MESSAGE,
    ACCESS_DENIED_MESSAGE,
    PROJECT_ALREADY_CLOSED_MESSAGE,
    SKILL_SEARCH_LIMIT,
)


def _require_post(request):
    """Возвращает JsonResponse с ошибкой, если метод не POST, иначе None."""
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )
    return None


def _require_owner(project, user):
    """Возвращает JsonResponse с ошибкой, если user не владелец проекта, иначе None."""
    if project.owner != user:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": ACCESS_DENIED_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )
    return None


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        qs = get_project_queryset().order_by("-created_at")
        skill = self.request.GET.get("skill")
        if skill:
            qs = qs.filter(skills__name=skill)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_skills"] = Skill.objects.values_list("name", flat=True).distinct()
        context["active_skill"] = self.request.GET.get("skill", "")
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return get_project_queryset()


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class ProjectUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


@login_required
def complete_project(request, pk):
    error = _require_post(request)
    if error:
        return error

    project = get_object_or_404(Project, pk=pk)

    error = _require_owner(project, request.user)
    if error:
        return error

    if project.status != ProjectStatus.OPEN:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": PROJECT_ALREADY_CLOSED_MESSAGE},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = ProjectStatus.CLOSED
    project.save(update_fields=["status"])

    return JsonResponse(
        {"status": OK_STATUS, "project_status": ProjectStatus.CLOSED},
        status=HTTPStatus.OK,
    )


@login_required
def toggle_participate(request, pk):
    error = _require_post(request)
    if error:
        return error

    project = get_object_or_404(Project, pk=pk)

    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse(
        {"status": OK_STATUS, "participant": not is_participant},
        status=HTTPStatus.OK,
    )


@login_required
def skill_search(request):
    search_query = request.GET.get("q", "").strip()
    if not search_query:
        return JsonResponse([], safe=False)
    skills = Skill.objects.filter(name__icontains=search_query)[:SKILL_SEARCH_LIMIT]
    return JsonResponse([{"id": s.id, "name": s.name} for s in skills], safe=False)


@login_required
def skill_add(request, pk):
    error = _require_post(request)
    if error:
        return error

    project = get_object_or_404(Project, pk=pk)

    error = _require_owner(project, request.user)
    if error:
        return error

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {"status": ERROR_STATUS, "message": "Неверный формат данных"},
            status=HTTPStatus.BAD_REQUEST,
        )

    skill_id = body.get("skill_id")
    name = body.get("name", "").strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, _ = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": "Укажите skill_id или name"},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name}, status=HTTPStatus.OK)


@login_required
def skill_remove(request, pk, skill_id):
    error = _require_post(request)
    if error:
        return error

    project = get_object_or_404(Project, pk=pk)

    error = _require_owner(project, request.user)
    if error:
        return error

    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": OK_STATUS}, status=HTTPStatus.OK)
