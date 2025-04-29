from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AuthError(HTTPException):
    def __init__(self, detail: Any = None, headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class ClientException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str = None):
        super().__init__(status_code=status_code, detail=message)
        self.code = code