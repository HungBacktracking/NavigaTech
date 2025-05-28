from enum import Enum
from starlette import status

from app.exceptions.errors.CustomClientException import ClientException


class CustomError(Enum):
    CHAT_ENGINE_ERROR = (status.HTTP_500_INTERNAL_SERVER_ERROR, "100", "Chat engine could not initialized")
    INVALID_VALUE = (status.HTTP_400_BAD_REQUEST, "17", "Invalid input value.")
    INTERNAL_SERVER_ERROR = (status.HTTP_500_INTERNAL_SERVER_ERROR, "100", "Internal server error")
    NOT_FOUND = (status.HTTP_404_NOT_FOUND, "10", "The resource could not be found")
    DUPLICATE_RESOURCE = (status.HTTP_409_CONFLICT, "11", "The resource already exists")
    INVALID_FILE_TYPE = (status.HTTP_400_BAD_REQUEST, "12", "Invalid file type")
    EXISTING_RESOURCE = (status.HTTP_409_CONFLICT, "13", "The resource already exists")
    INVALID_CREDENTIALS = (status.HTTP_401_UNAUTHORIZED, "14", "Incorrect email or password")
    SERVICE_UNAVAILABLE = (status.HTTP_503_SERVICE_UNAVAILABLE, "15", "Service temporarily unavailable")
    MESSAGE_DELIVERY_FAILED = (status.HTTP_500_INTERNAL_SERVER_ERROR, "16", "Failed to deliver message")
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
