# repository/order_book_repo.py
from typing import Optional, List

from domain.company import Company
from domain.order import Order, Side
from abc import ABC, abstractmethod

from repository.baseRepo import Repository, T, DbRepository

class OrderBookRepo(Repository, ABC):
    @abstractmethod
    def get_best(self, side: Side) -> Optional[Order]: ...

    @abstractmethod
    def get_by_side(self, side: Side) -> List[Order]: ...

    @abstractmethod
    def update_by_id(self, order: Order) -> bool: ...

    @abstractmethod
    def delete_best(self, side: Side) -> Optional[Order]: ...

class InMemoryOrderBookRepo(OrderBookRepo):
    def __init__(self, company: Company) -> None:
        self.company = company

    @property
    def _cb(self): #company.order_book
        return self.company.order_book

    def add(self, order: Order) -> None:
        self._cb.add_order(order)

    def adds(self, *orders: Order) -> None:
        for order in orders:
            self.add(order)

    def get_by_id(self, order_id: str) -> Optional[Order]:
        for o in self._cb.sells:
            if o.id == order_id:
                return o
        for o in self._cb.buys:
            if o.id == order_id:
                return o
        return None

    def remove(self, order_id: str) -> None:
        self._cb.remove_order(order_id)

    def list_all(self) -> List[Order]:
        return list(self._cb.sells) + list(self._cb.buys)

    def get_best(self, side: Side) -> Optional[Order]:
        return self._cb.get_best(side)

    def get_by_side(self, side: Side) -> List[Order]:
        return self._cb.get_by_side(side)

    def update_by_id(self, order: Order) -> bool:
        return self._cb.update_order(order)

    def delete_best(self, side: Side) -> Optional[Order]:
        return self._cb.delete_best(side)