import re
from urllib.parse import urlparse

from django import forms

from .constants import ALLOWED_GITHUB_DOMAINS, PHONE_REGEX


def validate_github_url_domain(github_url: str) -> None:
    parsed = urlparse(github_url)
    domain = parsed.netloc.lower()
    if domain not in ALLOWED_GITHUB_DOMAINS:
        raise forms.ValidationError("Введите корректную ссылку на GitHub.")


def validate_phone_format(phone: str) -> None:
    if not re.fullmatch(PHONE_REGEX, phone):
        raise forms.ValidationError(
            "Введите корректный номер телефона: 8XXXXXXXXXX или +7XXXXXXXXXX."
        )
