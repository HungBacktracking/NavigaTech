from contextlib import AbstractContextManager
from typing import Callable, Optional
from uuid import UUID

from sqlmodel import Session, select
from app.model.user_file import UserFile
from app.repository.base_repository import BaseRepository



class UserFileRepository(BaseRepository):
    def __init__(
        self, 
        session_factory: Callable[..., AbstractContextManager[Session]],
        replica_session_factory: Callable[..., AbstractContextManager[Session]] = None
    ):
        super().__init__(session_factory, UserFile, replica_session_factory)

    def get_by_user_and_type(self, user_id: UUID, file_type: str) -> Optional[UserFile]:
        with self.replica_session_factory() as session:
            stmt = select(UserFile).where(
                UserFile.user_id == user_id,
                UserFile.file_type == file_type
            )

            return session.scalars(stmt).first()