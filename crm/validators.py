from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Polish phone number validator
# Accepts formats like: +48 123 456 789, 48 123-456-789, 123 456 789, 123456789
phone_regex = RegexValidator(
    regex=r'^(?:\+?48)?[ -]?(?:\d{3}[ -]?\d{3}[ -]?\d{3}|\d{9})$',
    message=_("Wprowadź poprawny numer telefonu. Format: '+48 123 456 789' lub '123456789'.")
)
