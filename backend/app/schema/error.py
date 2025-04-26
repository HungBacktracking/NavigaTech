from pydantic import BaseModel
from typing import Optional

class ErrorResponse(BaseModel):
    code: str
    message: Optional[str] = None
