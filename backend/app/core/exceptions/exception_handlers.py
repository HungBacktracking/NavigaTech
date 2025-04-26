from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from app.core.exceptions.custom_error import CustomError
from app.core.exceptions.exceptions import ClientException, AuthError
from app.schema.error import ErrorResponse


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ClientException)
    async def client_exception_handler(request: Request, exc: ClientException):
        payload = ErrorResponse(message=exc.detail, code=exc.code)

        return JSONResponse(status_code=exc.status_code, content=payload.dict())

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        err = CustomError.INTERNAL_SERVER_ERROR
        payload = ErrorResponse(message=err.message, code=err.code)

        return JSONResponse(status_code=err.http_status, content=payload.dict())
