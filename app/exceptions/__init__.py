from fastapi import FastAPI

from app.exceptions.auth import register_exception_handlers as register_auth_handlers
from app.exceptions.base import register_exception_handlers as register_base_handlers
from app.exceptions.user import register_exception_handlers as register_user_handlers


def register_exception_handlers(app: FastAPI) -> None:
    register_base_handlers(app)
    register_auth_handlers(app)
    register_user_handlers(app)
