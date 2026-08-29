from src.email_validator import is_valid_email

def test_valid_email():
    assert is_valid_email("user@example.com") is True

def test_invalid_email():
    assert is_valid_email("not-an-email") is False
