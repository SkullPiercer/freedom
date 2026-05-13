from functools import wraps

from fastapi import Response

from app.core.config import settings


def set_auth_cookies(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response: Response | None = kwargs.get("response")

        if response is None:
            raise RuntimeError("Response dependency is required for set_auth_cookies")

        result = await func(*args, **kwargs)

        response.set_cookie(
            key="access_token",
            value=result.access_token,
            httponly=True,
            secure=settings.COOKIE.SECURE,
            samesite=settings.COOKIE.SAMESITE,
            max_age=settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            secure=settings.COOKIE.SECURE,
            samesite=settings.COOKIE.SAMESITE,
            max_age=settings.JWT.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        )

        return result

    return wrapper


def clear_auth_cookies(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response: Response | None = kwargs.get("response")

        if response is None:
            raise RuntimeError("Response dependency is required for clear_auth_cookies")

        result = await func(*args, **kwargs)

        response.delete_cookie(
            key="access_token",
            secure=settings.COOKIE.SECURE,
            samesite=settings.COOKIE.SAMESITE,
        )
        response.delete_cookie(
            key="refresh_token",
            secure=settings.COOKIE.SECURE,
            samesite=settings.COOKIE.SAMESITE,
        )

        return result

    return wrapper
