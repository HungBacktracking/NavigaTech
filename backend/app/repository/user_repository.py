from contextlib import AbstractContextManager
from typing import Callable, Optional
from sqlmodel import Session, select
from app.model.user import User
from app.repository.base_repository import BaseRepository



class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = User
        super().__init__(session_factory, User)


    def find_by_email(self, email) -> Optional[User]:
        with self.session_factory() as session:
            statement = select(User).where(User.email == email)
            return session.scalars(statement).first()

