from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session
from app.model.user import User
from app.repository.base_repository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = User
        super().__init__(session_factory, User)

    def create(self, user):
        with self.session_factory() as session:
            query = self.model(**user.dict())

            session.add(query)
            session.commit()
            session.refresh(query)

            return query

    def find_by_id(self, user_id):
        with self.session_factory() as session:
            query = session.query(self.model)
            user = query.filter(self.model.id == user_id).first()

            return user

    def update(self, user_id, update_request):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == user_id).update(update_request.dict(exclude_none=True))
            session.commit()

            return self.find_by_id(user_id)

    def find_by_email(self, email):
        with self.session_factory() as session:
            query = session.query(self.model)
            user = query.filter(self.model.email == email).first()

            return user

