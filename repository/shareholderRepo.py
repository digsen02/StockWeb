# repository/shareholder_repo.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from repository.baseRepo import Repository, DbRepository
from domain.shareholder import Shareholder


class ShareholderRepo(Repository[Shareholder], ABC):

    @abstractmethod
    def get_by_user_and_market(self, user_id: str, market_id: str) -> Optional[Shareholder]: ...

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> Optional[Shareholder]: ...

class InMemoryShareholderRepo(ShareholderRepo):

    def get_by_user_and_market(self, user_id: str, market_id: str) -> Optional[Shareholder]:
        pass

    def get_by_user_id(self, user_id: str) -> Optional[Shareholder]:
        pass

    def __init__(self) -> None:
        self.shareholders: Dict[str, Shareholder] = {}

    def add(self, shareholder: Shareholder) -> None:
        self.shareholders[shareholder.id] = shareholder

    def adds(self, *shareholders: Shareholder) -> None:
        for shareholder in shareholders:
            self.add(shareholder)

    def get_by_id(self, shareholder_id: str) -> Optional[Shareholder]:
        return self.shareholders.get(shareholder_id)

    def remove(self, shareholder_id: str) -> None:
        self.shareholders.pop(shareholder_id, None)

    def list_all(self) -> List[Shareholder]:
        return list(self.shareholders.values())

class DbShareholderRepo(ShareholderRepo, DbRepository[Shareholder]):
    def add(self, shareholder: Shareholder) -> None:
        sql = """
        INSERT INTO shareholders (
            id, user_id, market_id,
            cash_balance, portfolio_value, role
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        shareholder.id,
                        shareholder.user_id,
                        shareholder.market_id,
                        shareholder.cash_balance,
                        shareholder.portfolio_value,
                        shareholder.role,
                    ),
                )

    def adds(self, *shareholders: Shareholder) -> None:
        for _shareholder in shareholders:
            self.add(_shareholder)

    def get_by_id(self, shareholder_id: str) -> Optional[Shareholder]:
        sql = """
        SELECT id, user_id, market_id,
               cash_balance, portfolio_value
        FROM shareholders
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (shareholder_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Shareholder(
            id=row["id"],
            user_id=row["user_id"],
            market_id=row["market_id"],
            cash_balance=row["cash_balance"],
            portfolio_value=row["portfolio_value"],
            role=row["role"],
        )

    def get_by_user_and_market(self, user_id: str, market_id: str) -> Optional[Shareholder]:
        sql = """
        SELECT id, user_id, market_id,
               cash_balance, portfolio_value, role
        FROM shareholders
        WHERE user_id = %s AND market_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id, market_id))
                row = cur.fetchone()
        if not row:
            return None
        return Shareholder(
            id=row["id"],
            user_id=row["user_id"],
            market_id=row["market_id"],
            cash_balance=row["cash_balance"],
            portfolio_value=row["portfolio_value"],
            role=row["role"],
        )

    def get_by_user_id(self, user_id: str) -> List[Shareholder]:
        sql = """
        SELECT id, user_id, market_id,
               cash_balance, portfolio_value, role
        FROM shareholders
        WHERE user_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (user_id,))
                rows = cur.fetchall()
        return [
            Shareholder(
                id=row["id"],
                user_id=row["user_id"],
                market_id=row["market_id"],
                cash_balance=row["cash_balance"],
                portfolio_value=row["portfolio_value"],
                role=row["role"],
            )
            for row in rows
        ]

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM shareholders WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[Shareholder]:
        sql = """
        SELECT id, user_id, market_id,
               cash_balance, portfolio_value, role
        FROM shareholders
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            Shareholder(
                id=row["id"],
                user_id=row["user_id"],
                market_id=row["market_id"],
                cash_balance=row["cash_balance"],
                portfolio_value=row["portfolio_value"],
                role=row["role"],
            )
            for row in rows
        ]