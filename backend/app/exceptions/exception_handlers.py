from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.exceptions.custom_error import CustomError
from app.exceptions.errors.CustomClientException import ClientException
from fastapi.exceptions import RequestValidationError
from app.schema.error import ErrorResponse



def register_exception_handlers(app: FastAPI):
    @app.exception_handler(ClientException)
    async def client_exception_handler(request: Request, exc: ClientException):
        payload = ErrorResponse(message=exc.detail, code=exc.code)

        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        first_err = exc.errors()[0]
        code = "50"
        message = f"{first_err['loc'][-1]}: {first_err['msg']}"
        payload = ErrorResponse(code=code, message=message)

        return JSONResponse(status_code=400, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        err = CustomError.INTERNAL_SERVER_ERROR.as_exception()
        payload = ErrorResponse(message=err.detail, code=err.code)

        return JSONResponse(status_code=err.status_code, content=payload.model_dump())
