from contextlib import AbstractContextManager
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select
from app.model.skill import Skill
from app.repository.base_repository import BaseRepository


class SkillRepository(BaseRepository):
    def __init__(
        self, 
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None
    ):
        super().__init__(session_factory, Skill, replica_session_factory)

    def find_by_user_id(self, user_id: UUID) -> list[Skill]:
        with self.replica_session_factory() as session:
            statement = (
                select(Skill)
                .where(Skill.user_id == user_id)
            )

            return list(session.scalars(statement).all())