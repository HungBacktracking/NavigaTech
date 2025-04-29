from typing import Protocol


class RepositoryProtocol(Protocol):
    pass


class BaseService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self._repository = repository

    def close_scoped_session(self):
        self._repository.close_scoped_session()