"""Unit tests for authentication utilities."""

from utils.auth_utils import generate_remember_token, hash_password, verify_password
from utils.validators import validate_email, validate_prompt_not_empty


def test_hash_and_verify_password():
    password = "SecurePass123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_generate_remember_token():
    token1 = generate_remember_token()
    token2 = generate_remember_token()
    assert token1 != token2
    assert len(token1) > 20


def test_validate_email():
    assert validate_email("user@example.com")
    assert not validate_email("invalid-email")


def test_validate_prompt_not_empty():
    assert validate_prompt_not_empty("Hello")
    assert not validate_prompt_not_empty("   ")
