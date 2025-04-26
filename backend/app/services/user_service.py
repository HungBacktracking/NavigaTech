from app.core.exceptions import NotFoundError
from app.model.user import User
from app.repository.user_repository import UserRepository
from app.services.base_service import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        super().__init__(user_repository)

    def get_by_id(self, user_id):
        user: User = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundError(detail=f"not found id : {user_id}")

        return user.to_response()

    def update(self, user_id, update_request):
        updated_user: User = self.user_repository.update(user_id, update_request)
        if not updated_user:
            raise NotFoundError(detail=f"not found id : {user_id}")

        return updated_user.to_response()



