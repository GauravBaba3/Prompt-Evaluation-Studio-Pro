"""User authentication service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.models import User
from models.schemas import UserCreate, UserLogin, UserOut
from utils.auth_utils import generate_remember_token, hash_password, verify_password
from utils.exceptions import AuthenticationError, ValidationError
from utils.logger import get_logger
from utils.validators import validate_email

logger = get_logger(__name__)


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def register(self, data: UserCreate) -> UserOut:
        if not validate_email(data.email):
            raise ValidationError("Invalid email address.")
        existing = (
            self.session.query(User)
            .filter((User.username == data.username) | (User.email == data.email))
            .first()
        )
        if existing:
            raise ValidationError("Username or email already exists.")

        user = User(
            username=data.username.strip(),
            email=data.email.strip().lower(),
            password_hash=hash_password(data.password),
            is_admin=False,
            theme="light",
        )
        self.session.add(user)
        self.session.flush()
        logger.info("Registered user: %s", user.username)
        return UserOut.model_validate(user)

    def login(self, data: UserLogin) -> tuple[UserOut, str | None]:
        user = self.session.query(User).filter(User.username == data.username.strip()).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid username or password.")

        user.last_login = datetime.now(timezone.utc)
        remember_token = None
        if data.remember:
            remember_token = generate_remember_token()
            user.remember_token = remember_token
        self.session.flush()
        logger.info("User logged in: %s", user.username)
        return UserOut.model_validate(user), remember_token

    def get_user_by_id(self, user_id: int) -> UserOut | None:
        user = self.session.query(User).filter(User.id == user_id).first()
        return UserOut.model_validate(user) if user else None

    def get_user_by_remember_token(self, token: str) -> UserOut | None:
        user = self.session.query(User).filter(User.remember_token == token).first()
        return UserOut.model_validate(user) if user else None

    def update_theme(self, user_id: int, theme: str) -> UserOut:
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            raise AuthenticationError("User not found.")
        user.theme = theme
        self.session.flush()
        return UserOut.model_validate(user)

    def logout(self, user_id: int) -> None:
        user = self.session.query(User).filter(User.id == user_id).first()
        if user:
            user.remember_token = None
            self.session.flush()
