from enum import Enum
from starlette import status
from .exceptions import ClientException

class CustomError(Enum):
    NOT_FOUND = (status.HTTP_404_NOT_FOUND, "10", "The resource could not be found")
    DUPLICATE_RESOURCE = (status.HTTP_409_CONFLICT, "11", "The resource already exists")
    # …

    def __init__(self, http_status: int, code: str, message: str):
        self.http_status = http_status
        self.code = code
        self.message = message

    def as_exception(self):
        return ClientException(
            status_code=self.http_status,
            code=self.code,
            message=self.message
        )
