from urllib.parse import urlparse

from django import forms

from .constants import ALLOWED_GITHUB_DOMAINS


def validate_github_url_domain(github_url: str) -> None:
    parsed = urlparse(github_url)
    domain = parsed.netloc.lower()
    if domain not in ALLOWED_GITHUB_DOMAINS:
        raise forms.ValidationError("Введите корректную ссылку на GitHub.")
