from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select

from app.model.award import Award
from app.repository.base_repository import BaseRepository


class AwardRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = Award
        super().__init__(session_factory, Award)


    def find_by_user_id(self, user_id: UUID) -> list[Award]:
        with self.session_factory() as session:
            statement = (
                select(Award)
                .where(Award.user_id == user_id)
                .order_by(Award.date.desc())
            )

            return list(session.scalars(statement).all())