from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exceptions.base import BaseAppException

class UserNotFoundException(BaseAppException):
    detail = "User not found!"


class InvalidPasswordException(BaseAppException):
    detail = "Invalid login or password!"


async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundException,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )


async def invalid_password_exception_handler(
    request: Request,
    exc: InvalidPasswordException,
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        UserNotFoundException,
        user_not_found_exception_handler
    )
    app.add_exception_handler(
        InvalidPasswordException,
        invalid_password_exception_handler,
    )
