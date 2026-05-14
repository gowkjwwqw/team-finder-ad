from django import forms

from .validators import validate_github_url_domain


class GithubUrlCleanMixin:
    github_url_model = None

    def clean_github_url(self):
        github_url = (self.cleaned_data.get("github_url") or "").strip()

        if not github_url:
            return github_url

        validate_github_url_domain(github_url)
        normalized_url = github_url.rstrip("/")

        qs = self.github_url_model.objects.filter(github_url=normalized_url)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                "Профиль пользователя с данной ссылкой на профиль GitHub уже существует."
            )

        return normalized_url
