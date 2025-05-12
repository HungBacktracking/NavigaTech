from typing import Optional
from uuid import UUID
from fastapi import WebSocket
from app.model.user import User



from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import jwt
from pydantic import ValidationError

from app.core.config import configs
from app.core.containers.application_container import ApplicationContainer
from app.core.security import ALGORITHM, JWTBearer
from app.exceptions.errors.CustomClientException import AuthError
from app.schema.auth_schema import Payload
from app.schema.user_schema import UserBasicResponse
from app.services.user_service import UserService

@inject
def get_current_user(
    token: str = Depends(JWTBearer()),
    service: UserService = Depends(Provide[ApplicationContainer.services.user_service]),
) -> UserBasicResponse:
    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        token_data = Payload(**payload)
    except (jwt.JWTError, ValidationError):
        raise AuthError(detail="Could not validate credentials")

    current_user: UserBasicResponse = service.get_by_id(token_data.id)
    if not current_user:
        raise AuthError(detail="User not found")

    return current_user


@inject
def get_ws_user(
    websocket: WebSocket,
    service: UserService = Depends(Provide[ApplicationContainer.services.user_service])
) -> Optional[UserBasicResponse]:
    """
    Validate WebSocket connection with JWT token
    """

    # Get token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=ALGORITHM)
        token_data = Payload(**payload)
    except (jwt.JWTError, ValidationError):
        raise AuthError(detail="Could not validate credentials")

    current_user: UserBasicResponse = service.get_by_id(token_data.id)
    if not current_user:
        raise AuthError(detail="User not found")

    return current_user



