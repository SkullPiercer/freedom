from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.exceptions.base import BaseAppException

class UserNotFoundException(BaseAppException):
    detail = "User not found!"


async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundException,
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.detail},
    )

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        UserNotFoundException,
        user_not_found_exception_handler
    )
