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
                 host: str | None = None,
                 port: int | None = None,
                 user: str | None = None,
                 password: str | None = None,
                 db: str | None = None):
        host = host if host is not None else os.getenv("MYSQLHOST")
        _port = port if port is not None else os.getenv("MYSQLPORT")
        user = user if user is not None else os.getenv("MYSQLUSER")
        password = password if password is not None else os.getenv("MYSQLPASSWORD")
        db = db if db is not None else os.getenv("MYSQLDATABASE")
        self._conn_params = {
            "host": host,
            "port": int(_port),
            "user": user,
            "password": password,
            "database": db,
            "cursorclass": DictCursor,
            "autocommit": True,
        }
    def _get_conn(self):
        return pymysql.connect(**self._conn_params)