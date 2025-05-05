from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select
from app.model.project import Project
from app.repository.base_repository import BaseRepository


class ProjectRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        self.model = Project
        super().__init__(session_factory, Project)

    def find_by_user_id(self, user_id: UUID) -> list[Project]:
        with self.session_factory() as session:
            statement = (
                select(Project)
                .where(Project.user_id == user_id)
                .order_by(Project.end_date.desc())
            )

            return list(session.scalars(statement).all())

