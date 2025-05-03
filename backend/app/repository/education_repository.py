from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select
from app.model.education import Education
from app.repository.base_repository import BaseRepository


class EducationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = Education
        super().__init__(session_factory, Education)


    def find_by_user_id(self, user_id: UUID) -> list[Education]:
        with self.session_factory() as session:
            statement = (
                select(Education)
                .where(Education.user_id == user_id)
                .order_by(Education.end_date.desc())
            )

            return list(session.scalars(statement).all())