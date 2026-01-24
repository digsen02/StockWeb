from abc import ABC, abstractmethod
from repository.baseRepo import Repository, DbRepository
from typing import Dict, Optional, List
from domain.portfolio import Portfolio

class PortfolioRepo(Repository[Portfolio] ,ABC):

    @abstractmethod
    def get_by_shareholder_id(self, shareholder_id: str) -> Optional[Portfolio]: ...

    @abstractmethod
    def update(self, portfolio: Portfolio) -> None: ...

class InmemoryPortfolioRepo(PortfolioRepo):
    def __init__(self) -> None:
        self.portfolios: Dict[str, Portfolio] = {}

    def add(self, portfolio: Portfolio) -> None:
        self.portfolios[portfolio.id] = portfolio

    def adds(self, *portfolios: Portfolio) -> None:
        for p in portfolios:
            self.add(p)

    def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        return self.portfolios.get(portfolio_id)

    def get_by_shareholder_id(self, shareholder_id: str) -> Optional[Portfolio]:
        for p in self.portfolios.values():
            if p.shareholder_id == shareholder_id:
                return p
        return None

    def remove(self, portfolio_id: str) -> None:
        self.portfolios.pop(portfolio_id, None)

    def list_all(self) -> List[Portfolio]:
        return list(self.portfolios.values())

    def update(self, portfolio: Portfolio) -> None:
        self.portfolios[portfolio.id] = portfolio


class DbPortfolioRepo(PortfolioRepo, DbRepository[Portfolio]):
    def add(self, portfolio: Portfolio) -> None:
        sql = """
        INSERT INTO portfolios (
            id, shareholder_id,
            cash_balance, portfolio_value
        )
        VALUES (%s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        portfolio.id,
                        portfolio.shareholder_id,
                        portfolio.cash_balance,
                        portfolio.portfolio_value,
                    ),
                )

    def adds(self, *portfolios: Portfolio) -> None:
        for _portfolio in portfolios:
            self.add(_portfolio)

    def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        sql = """
        SELECT id, shareholder_id,
               cash_balance, portfolio_value
        FROM portfolios
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (portfolio_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Portfolio(
            id=row["id"],
            shareholder_id=row["shareholder_id"],
            cash_balance=row["cash_balance"],
            portfolio_value=row["portfolio_value"],
        )

    def get_by_shareholder_id(self, shareholder_id: str) -> Optional[Portfolio]:
        sql = """
        SELECT id, shareholder_id,
               cash_balance, portfolio_value
        FROM portfolios
        WHERE shareholder_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (shareholder_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Portfolio(
            id=row["id"],
            shareholder_id=row["shareholder_id"],
            cash_balance=row["cash_balance"],
            portfolio_value=row["portfolio_value"],
        )

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM portfolios WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[Portfolio]:
        sql = """
        SELECT id, shareholder_id,
               cash_balance, portfolio_value
        FROM portfolios
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            Portfolio(
                id=row["id"],
                shareholder_id=row["shareholder_id"],
                cash_balance=row["cash_balance"],
                portfolio_value=row["portfolio_value"],
            )
            for row in rows
        ]

    def update(self, portfolio: Portfolio) -> None:
        sql = """
        UPDATE portfolios
        SET cash_balance = %s,
            portfolio_value = %s
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        portfolio.cash_balance,
                        portfolio.portfolio_value,
                        portfolio.id,
                    ),
                )
