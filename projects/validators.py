from urllib.parse import urlparse

from django import forms

ALLOWED_GITHUB_DOMAINS = {"github.com", "www.github.com"}


def validate_github_url_domain(github_url: str) -> None:
    """Проверяет, что URL принадлежит github.com."""
    parsed = urlparse(github_url)
    domain = parsed.netloc.lower()
    if domain not in ALLOWED_GITHUB_DOMAINS:
        raise forms.ValidationError("Введите корректную ссылку на GitHub.")
