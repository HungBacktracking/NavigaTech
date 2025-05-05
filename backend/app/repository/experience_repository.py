from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select
from app.model.experience import Experience
from app.repository.base_repository import BaseRepository


class ExperienceRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = Experience
        super().__init__(session_factory, Experience)


    def find_by_user_id(self, user_id: UUID) -> list[Experience]:
        with self.session_factory() as session:
            statement = (
                select(Experience)
                .where(Experience.user_id == user_id)
                .order_by(Experience.end_date.desc())
            )

            return list(session.scalars(statement).all())