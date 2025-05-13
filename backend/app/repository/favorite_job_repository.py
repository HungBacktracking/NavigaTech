from contextlib import AbstractContextManager
from typing import Callable, Optional, List, Dict
from uuid import UUID

from sqlmodel import Session, select

from app.model.favorite_job import FavoriteJob
from app.repository.base_repository import BaseRepository


class FavoriteJobRepository(BaseRepository):
    def __init__(
        self,
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None,
    ):
        super().__init__(session_factory, FavoriteJob, replica_session_factory)

    def find_by_user_id(self, user_id: UUID) -> FavoriteJob:
        with self.replica_session_factory() as session:
            statement = select(FavoriteJob).where(FavoriteJob.user_id == user_id)

            return session.scalars(statement).first()

    def find_by_job_and_user_id(
        self, job_id: UUID, user_id: UUID
    ) -> Optional[FavoriteJob]:
        """Find a favorite job by job_id and user_id"""
        with self.replica_session_factory() as session:
            statement = (
                select(FavoriteJob)
                .where(FavoriteJob.job_id == job_id)
                .where(FavoriteJob.user_id == user_id)
            )

            return session.scalars(statement).first()

    def get_favorites_by_job_ids(self, job_ids: List[UUID], user_id: UUID) -> Dict[UUID, FavoriteJob]:
        favorites = {}
        if job_ids:
            with self.session_factory() as session:
                statement = select(FavoriteJob).where(
                    FavoriteJob.job_id.in_(job_ids),
                    FavoriteJob.user_id == user_id
                )
                results = session.execute(statement).scalars().all()
                favorites = {fav.job_id: fav for fav in results}

        return favorites
