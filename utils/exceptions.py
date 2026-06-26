"""Custom exceptions."""

from __future__ import annotations


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, code="AUTH_ERROR")


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class DatabaseError(AppError):
    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message, code="DATABASE_ERROR")


class GeminiAPIError(AppError):
    def __init__(self, message: str = "Gemini API error", code: str = "GEMINI_ERROR") -> None:
        super().__init__(message, code=code)


class RateLimitError(GeminiAPIError):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, code="RATE_LIMIT")


class TimeoutError(GeminiAPIError):
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message, code="TIMEOUT")


class JSONParseError(AppError):
    def __init__(self, message: str = "Failed to parse JSON response") -> None:
        super().__init__(message, code="JSON_PARSE_ERROR")
