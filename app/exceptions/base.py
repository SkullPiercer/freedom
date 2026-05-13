from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


class BaseAppException(Exception):
    detail = "An unexpected error occurred"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class BaseAppHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundException(BaseAppException):
    detail = "Object not found!"


class DataAlreadyExistsException(BaseAppException):
    detail = "Data already exists!"


async def data_already_exists_exception_handler(
    request: Request,
    exc: DataAlreadyExistsException,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DataAlreadyExistsException,
        data_already_exists_exception_handler,
    )
