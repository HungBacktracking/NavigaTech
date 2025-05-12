from contextlib import AbstractContextManager
from typing import Callable, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.model.favorite_job import FavoriteJob
from app.repository.base_repository import BaseRepository



class FavoriteJobRepository(BaseRepository):
    def __init__(
        self, 
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None
    ):
        super().__init__(session_factory, FavoriteJob, replica_session_factory)

    def find_by_user_id(self, user_id: UUID) -> FavoriteJob:
        with self.replica_session_factory() as session:
            statement = (
                select(FavoriteJob)
                .where(FavoriteJob.user_id == user_id)
            )

            return session.scalars(statement).first()
