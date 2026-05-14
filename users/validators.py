import re

from django import forms

from .constants import PHONE_REGEX


def validate_phone_format(phone: str) -> None:
    if not re.fullmatch(PHONE_REGEX, phone):
        raise forms.ValidationError(
            "Введите корректный номер телефона: 8XXXXXXXXXX или +7XXXXXXXXXX."
        )
