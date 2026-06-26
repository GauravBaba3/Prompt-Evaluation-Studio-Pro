"""Database and auth service tests."""

from backend.service_factory import get_services
from models.schemas import PromptCreate, UserCreate, UserLogin
from utils.exceptions import AuthenticationError, ValidationError


def test_user_registration_and_login():
    with get_services() as services:
        user = services.auth.register(
            UserCreate(username="testuser", email="test@example.com", password="password123")
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"

        logged_in, token = services.auth.login(UserLogin(username="testuser", password="password123", remember=True))
        assert logged_in.username == "testuser"
        assert token is not None


def test_login_invalid_credentials():
    with get_services() as services:
        services.auth.register(
            UserCreate(username="user2", email="user2@example.com", password="password123")
        )
        try:
            with get_services() as services2:
                services2.auth.login(UserLogin(username="user2", password="wrongpass"))
            assert False, "Should raise AuthenticationError"
        except AuthenticationError:
            pass


def test_duplicate_registration():
    with get_services() as services:
        services.auth.register(
            UserCreate(username="dupuser", email="dup@example.com", password="password123")
        )
        try:
            services.auth.register(
                UserCreate(username="dupuser", email="dup@example.com", password="password123")
            )
            assert False, "Should raise ValidationError"
        except ValidationError:
            pass


def test_prompt_crud():
    with get_services() as services:
        user = services.auth.register(
            UserCreate(username="promptuser", email="prompt@example.com", password="password123")
        )
        prompt = services.prompts.create(
            user.id,
            PromptCreate(title="Test Prompt", user_prompt="Hello {{name}}", category="General"),
        )
        assert prompt.title == "Test Prompt"
        assert prompt.current_version == 1

        fetched = services.prompts.get_by_id(user.id, prompt.id)
        assert fetched is not None
        assert fetched.user_prompt == "Hello {{name}}"

        services.prompts.create_version(user.id, prompt.id, "Updated version")
        updated = services.prompts.get_by_id(user.id, prompt.id)
        assert updated.current_version == 2

        versions = services.prompts.list_versions(user.id, prompt.id)
        assert len(versions) >= 2
