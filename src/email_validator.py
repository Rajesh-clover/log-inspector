import re

EMAIL_REGEX = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")

def is_valid_email(email: str) -> bool:
    """Return True if the given string is a valid email address."""
    return bool(EMAIL_REGEX.match(email))
