from abc import ABC
from typing import Optional, List

from domain.market import Market
from repository.baseRepo import Repository, DbRepository, T


class MarketRepo(Repository[Market], ABC): ...

class DbMarketRepo(MarketRepo, DbRepository[Market]):
    def add(self, market: Market) -> None:
        sql = "INSERT INTO markets (id, name, created_at) VALUES (%s, %s, %s)"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (market.id, market.name, market.created_at))

    def adds(self, *markets: Market) -> None:
        for market in markets:
            self.add(market)

    def get_by_id(self, market_id: str) -> Optional[Market]:
        sql = "SELECT id, name FROM markets WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (market_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Market(
            id=row["id"],
            name=row["name"],
        )

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM markets WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[Market]:
        sql = "SELECT id, name FROM markets"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            Market(
                id=row["id"],
                name=row["name"],
            )
            for row in rows
        ]