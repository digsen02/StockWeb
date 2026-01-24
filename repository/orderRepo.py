from abc import ABC, abstractmethod
from typing import Optional, List

from domain.order import Order, Side
from repository.baseRepo import Repository, T, DbRepository


class OrderRepo(Repository, ABC): ...

class DbOrderRepo(OrderRepo, DbRepository[Order]):

    def add(self, entity: Order) -> None:
        sql = """
        INSERT INTO orders (
            id, shareholder_id, company_id,
            side, quantity, price, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                print(f"id:{entity.id}")
                print(f"shareholder_id:{entity.shareholder_id}")
                print(f"company_id:{entity.company_id}")
                print(f"side.value:{entity.side.value}")
                print(f"quantity:{entity.quantity}")
                print(f"price:{entity.price}")
                print(f"created_at:{entity.created_at}")
                cur.execute(
                    sql,
                    (
                        entity.id,
                        entity.shareholder_id,
                        entity.company_id,
                        entity.side.value,  # "buy" / "sell"
                        entity.quantity,
                        entity.price,
                        entity.created_at,
                    ),
                )

    def adds(self, *entities: Order) -> None:
        for e in entities:
            self.add(e)

    def get_by_id(self, entity_id: str) -> Optional[Order]:
        sql = """
        SELECT id, shareholder_id, company_id,
               side, quantity, price, created_at
        FROM orders
        WHERE id = %s
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))
                row = cur.fetchone()
        if not row:
            return None
        return Order(
            shareholder_id=row["shareholder_id"],
            company_id=row["company_id"],
            side=Side(row["side"]),
            quantity=row["quantity"],
            price=row["price"],
            created_at=row["created_at"],
            id=row["id"],
        )

    def remove(self, entity_id: str) -> None:
        sql = "DELETE FROM orders WHERE id = %s"
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (entity_id,))

    def list_all(self) -> List[Order]:
        sql = """
        SELECT id, shareholder_id, company_id,
               side, quantity, price, created_at
        FROM orders
        """
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            Order(
                shareholder_id=row["shareholder_id"],
                company_id=row["company_id"],
                side=Side(row["side"]),
                quantity=row["quantity"],
                price=row["price"],
                created_at=row["created_at"],
                id=row["id"],
            )
            for row in rows
        ]