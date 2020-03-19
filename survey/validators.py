from django.core.exceptions import ValidationError


def validate_especial_charachters(value):
    """
    Ensures text fields does not include especial characters.
    """
    especial_charachters = ['*', '>', '<']

    for char in especial_charachters:
        if char in value:
            raise ValidationError('This field can not contain *, > or <.')
