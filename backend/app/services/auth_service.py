from datetime import timedelta

from app.core.config import configs

from app.core.security import create_access_token, get_password_hash, verify_password
from app.exceptions.custom_error import CustomError
from app.exceptions.errors.CustomClientException import AuthError
from app.model.user import User
from app.repository.user_repository import UserRepository
from app.schema.auth_schema import Payload, SignIn, SignUp
from sqlalchemy.exc import IntegrityError

from app.services.base_service import BaseService


class AuthService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def sign_in(self, sign_in_info: SignIn):
        user: User = self.user_repository.find_by_email(sign_in_info.email)
        if not user:
            raise AuthError(detail="Incorrect email or password")

        if not verify_password(sign_in_info.password, user.password):
            raise AuthError(detail="Incorrect email or password")

        payload = Payload(
            id=str(user.id),
            email=user.email
        )

        token_lifespan = timedelta(minutes=configs.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, expiration_datetime = create_access_token(payload.model_dump(), token_lifespan)

        sign_in_result = {
            "access_token": access_token,
            "expiration": expiration_datetime,
            "user_info": user,
        }

        return sign_in_result

    def sign_up(self, user_info: SignUp):
        user_info.password = get_password_hash(user_info.password)

        try:
            created_user = self.user_repository.create(user_info)
        except IntegrityError as e:
            raise CustomError.DUPLICATE_RESOURCE.as_exception()

        return created_user
