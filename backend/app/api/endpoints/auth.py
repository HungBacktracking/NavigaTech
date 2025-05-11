from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.containers.application_container import ApplicationContainer
from app.core.middleware import inject
from app.schema.auth_schema import SignIn, SignInResponse, SignUp
from app.schema.user_schema import UserBasicResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/sign-in", response_model=SignInResponse)
@inject
def sign_in(user_info: SignIn, service: AuthService = Depends(Provide[ApplicationContainer.services.provided.auth_service])):
    return service.sign_in(user_info)


@router.post("/sign-up", response_model=UserBasicResponse)
@inject
def sign_up(user_info: SignUp, service: AuthService = Depends(Provide[ApplicationContainer.services.provided.auth_service])):
    return service.sign_up(user_info)
