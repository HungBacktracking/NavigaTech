from contextlib import AbstractContextManager
from typing import Callable, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session
from app.model.base_model import BaseModel


T = TypeVar("T", bound=BaseModel)


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model: Type[T]) -> None:
        self.session_factory = session_factory
        self.model = model

    def create(self, create_request: T):
        with self.session_factory() as session:
            model_db = self.model.model_validate(create_request)

            session.add(model_db)
            session.commit()
            session.refresh(model_db)

            return model_db

    def find_by_id(self, model_id: UUID):
        with self.session_factory() as session:
            model = session.get(self.model, model_id)

            return model

    def update(self, model_id: UUID, update_request: T):
        with self.session_factory() as session:
            model_db = session.get(self.model, model_id)
            if not model_db:
                return None

            model_data = update_request.model_dump(exclude_unset=True)
            model_db.sqlmodel_update(Type[self.model], model_data)
            session.add(model_db)
            session.commit()
            session.refresh(model_db)

            return model_db

    def delete(self, model_id: UUID):
        with self.session_factory() as session:
            model_db = session.get(self.model, model_id)
            if not model_db:
                return None

            session.delete(model_db)
            session.commit()

            return model_db

    def close_scoped_session(self):
        with self.session_factory() as session:
            return session.close()
