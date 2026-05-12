import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .mixins import OwnerRequiredMixin
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


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        qs = (
            Project.objects.select_related("owner")
            .prefetch_related("participants", "skills")
            .order_by("-created_at")
        )
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
        return Project.objects.select_related("owner").prefetch_related("participants", "skills")


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
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


@login_required
def complete_project(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": ACCESS_DENIED_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

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
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse(
        {"status": OK_STATUS, "participant": participant},
        status=HTTPStatus.OK,
    )


@login_required
def skill_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse([], safe=False)
    skills = Skill.objects.filter(name__icontains=q)[:SKILL_SEARCH_LIMIT]
    return JsonResponse([{"id": s.id, "name": s.name} for s in skills], safe=False)


@login_required
def skill_add(request, pk):
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": ACCESS_DENIED_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

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
    if request.method != "POST":
        return JsonResponse(
            {"status": ERROR_STATUS, "message": METHOD_NOT_ALLOWED_MESSAGE},
            status=HTTPStatus.METHOD_NOT_ALLOWED,
        )

    project = get_object_or_404(Project, pk=pk)

    if project.owner != request.user:
        return JsonResponse(
            {"status": ERROR_STATUS, "message": ACCESS_DENIED_MESSAGE},
            status=HTTPStatus.FORBIDDEN,
        )

    skill = get_object_or_404(Skill, pk=skill_id)
    project.skills.remove(skill)
    return JsonResponse({"status": OK_STATUS}, status=HTTPStatus.OK)
