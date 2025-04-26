from contextlib import AbstractContextManager
from typing import Callable, Type, TypeVar
from sqlalchemy.orm import Session
from app.model.base_model import BaseModel


T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model: Type[T]) -> None:
        self.session_factory = session_factory
        self.model = model

    def close_scoped_session(self):
        with self.session_factory() as session:
            return session.close()
