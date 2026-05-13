from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions.base import BaseAppException


class InvalidTokenException(BaseAppException):
    detail = "Invalid or expired token"


async def invalid_token_exception_handler(
    request: Request,
    exc: InvalidTokenException,
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        InvalidTokenException,
        invalid_token_exception_handler,
    )
