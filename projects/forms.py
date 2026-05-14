from django import forms

from core.mixins import GithubUrlCleanMixin
from .models import Project


class ProjectForm(GithubUrlCleanMixin, forms.ModelForm):
    github_url_model = Project

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
