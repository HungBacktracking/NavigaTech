from typing import Protocol


class RepositoryProtocol(Protocol):
    pass


class BaseService:
    def __init__(self, *repositories: RepositoryProtocol) -> None:
        self._repositories = repositories

    def close_scoped_session(self):
        for repo in self._repositories:
            try:
                repo.close_scoped_session()
            except AttributeError:
                pass