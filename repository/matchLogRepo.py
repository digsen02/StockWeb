from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal

from domain.log import MatchLog
from repository.baseRepo import Repository, DbRepository, T


class MatchLogRepo(Repository[MatchLog], ABC):

    @abstractmethod
    def get_by_time(self, time: datetime) -> List[MatchLog]: ...

    @abstractmethod
    def get_by_buy_order_id(self, buy_order_id: str) -> List[MatchLog]: ...

    @abstractmethod
    def get_by_sell_order_id(self, sell_order_id: str) -> List[MatchLog]: ...


class InMemoryMatchLogRepo(MatchLogRepo):
    def __init__(self):
        self.logs: Dict[str, MatchLog] = {}

    def add(self, match_log: MatchLog) -> None:
        self.logs[match_log.id] = match_log

    def adds(self, *match_logs: MatchLog) -> None:
        for log in match_logs:
            self.add(log)

    def remove(self, match_log_id: str) -> bool:
        return self.logs.pop(match_log_id, None) is not None

    def get_by_id(self, match_log_id: str) -> Optional[MatchLog]:
        return self.logs.get(match_log_id)

    def get_by_time(self, time: datetime) -> List[MatchLog]:
        return [log for log in self.logs.values() if log.created_at == time]

    def get_by_buy_order_id(self, buy_order_id: str) -> List[MatchLog]:
        return [log for log in self.logs.values() if log.buy_order_id == buy_order_id]

    def get_by_sell_order_id(self, sell_order_id: str) -> List[MatchLog]:
        return [log for log in self.logs.values() if log.sell_order_id == sell_order_id]

    def list_all(self) -> List[MatchLog]:
        return list(self.logs.values())


class DbMatchLogRepo(MatchLogRepo, DbRepository[MatchLog]):
    test = [id,]

    def add(self, match_log: MatchLog) -> None:
        sql = """
        INSERT INTO match_logs (
            id, buy_order_id, sell_order_id,
            price, quantity, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        match_log.id,
                        match_log.buy_order_id,
                        match_log.sell_order_id,
                        match_log.price,
                        match_log.quantity,
                        match_log.created_at,
                    ),
                )

    def adds(self, *match_logs: MatchLog) -> None:
        for log in match_logs:
            self.add(log)

    def get_by_id(self, match_log_id: str) -> Optional[MatchLog]:
        sql = """
        SELECT id, buy_order_id, sell_order_id,
               price, quantity, created_at
        FROM match_logs
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (match_log_id,))
                row = cur.fetchone()
        if not row:
            return None

        return MatchLog(
            id=row["id"],
            buy_order_id=row["buy_order_id"],
            sell_order_id=row["sell_order_id"],
            price=row["price"],
            quantity=row["quantity"],
            created_at=row["created_at"],
        )

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM match_logs WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[MatchLog]:
        sql = """
        SELECT id, buy_order_id, sell_order_id,
               price, quantity, created_at
        FROM match_logs
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            MatchLog(
                id=row["id"],
                buy_order_id=row["buy_order_id"],
                sell_order_id=row["sell_order_id"],
                price=row["price"],
                quantity=row["quantity"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_by_time(self, time: datetime) -> List[MatchLog]:
        sql = """
        SELECT id, buy_order_id, sell_order_id,
               price, quantity, created_at
        FROM match_logs
        WHERE created_at = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (time,))
                rows = cur.fetchall()
        return [
            MatchLog(
                id=row["id"],
                buy_order_id=row["buy_order_id"],
                sell_order_id=row["sell_order_id"],
                price=row["price"],
                quantity=row["quantity"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_by_buy_order_id(self, buy_order_id: str) -> List[MatchLog]:
        sql = """
        SELECT id, buy_order_id, sell_order_id,
               price, quantity, created_at
        FROM match_logs
        WHERE buy_order_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (buy_order_id,))
                rows = cur.fetchall()
        return [
            MatchLog(
                id=row["id"],
                buy_order_id=row["buy_order_id"],
                sell_order_id=row["sell_order_id"],
                price=row["price"],
                quantity=row["quantity"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_by_sell_order_id(self, sell_order_id: str) -> List[MatchLog]:
        sql = """
        SELECT id, buy_order_id, sell_order_id,
               price, quantity, created_at
        FROM match_logs
        WHERE sell_order_id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (sell_order_id,))
                rows = cur.fetchall()
        return [
            MatchLog(
                id=row["id"],
                buy_order_id=row["buy_order_id"],
                sell_order_id=row["sell_order_id"],
                price=row["price"],
                quantity=row["quantity"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
