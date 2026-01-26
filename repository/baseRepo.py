# repository/baseRepo.py
import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from pymysql.cursors import DictCursor
import pymysql
import dotenv

T = TypeVar("T")

class Repository(Generic[T], ABC):

    @abstractmethod
    def add(self, entity: T) -> None:
        ...

    @abstractmethod
    def adds(self, *entities: T) -> None:
        for _entity in entities:
            self.add(_entity)

    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        ...

    @abstractmethod
    def remove(self, entity_id: str) -> None:
        ...

    @abstractmethod
    def list_all(self) -> List[T]:
        ...

class DbRepository(Repository[T], ABC):
    dotenv.load_dotenv()

    def __init__(self,
                 host: str = os.getenv("HOST"),
                 port: int = int(os.getenv("PORT")),
                 user: str = os.getenv("USER"),
                 password: str = os.getenv("PASSWORD"),
                 db: str = os.getenv("DB")):
        self._conn_params = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": db,
            "cursorclass": DictCursor,
            "autocommit": True,
        }
    def _get_conn(self):
        return pymysql.connect(**self._conn_params)