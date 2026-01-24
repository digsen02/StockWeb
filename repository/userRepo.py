from abc import ABC, abstractmethod
from typing import Optional, Dict, List


from .baseRepo import Repository, DbRepository
from domain.user import User



class UserRepo(Repository[User], ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        ...


class InMemoryUserRepo(UserRepo):

    def __init__(self):
        self._users_by_id: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    def add(self, user: User) -> None:
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user

    def adds(self, *users: User) -> None:
        for user in users:
            self.add(user)

    def remove(self, user_id: str) -> None:
        user = self._users_by_id.pop(user_id, None)
        if user:
            self._users_by_email.pop(user.email, None)

    def list_all(self) -> List[User]:
        return list(self._users_by_id.values())

    def get_by_email(self, email: str) -> Optional[User]:
        return self._users_by_email.get(email)

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users_by_id.get(user_id)

class DbUserRepo(DbRepository[User], UserRepo):
    def add(self, user: User) -> None:
        sql = """
        INSERT INTO users (id, nickname, email, password_hash, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user.id, user.nickname, user.email, user.password_hash, user.created_at))

    def adds(self, *users: User) -> None:
        for user in users:
            self.add(user)

    def get_by_id(self, user_id: str) -> Optional[User]:
        sql = "SELECT id, email, nickname, password_hash, created_at FROM users WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id,))
                row = cur.fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            nickname=row["nickname"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
        )

    def get_by_email(self, email: str) -> Optional[User]:
        sql = "SELECT id, email, nickname, password_hash, created_at FROM users WHERE email = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (email,))
                row = cur.fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            nickname=row["nickname"],
            password_hash=row["password_hash"],
            created_at=row["created_at"],
        )

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM users WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[User]:
        sql = "SELECT id, email, nickname, password_hash, created_at FROM users WHERE email = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            User(
                id=row["id"],
                email=row["email"],
                nickname=row["nickname"],
                password_hash=row["password_hash"],
                created_at=row["created_at"],
            )
            for row in rows
        ]