from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from .common import new_id

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(str, Enum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"

# "ENUM('OPEN','PARTIAL','FILLED','CANCELLED')"

@dataclass
class Order:
    shareholder_id: Optional[str] # FK
    company_id: str # FK

    side: Side
    quantity: int
    price: Decimal
    created_at: datetime = field(default_factory=datetime.now)
    status: OrderStatus = OrderStatus.OPEN.value
    filled_quantity: int = 0
    id: str = field(default_factory=new_id) # PK

class OrderBook:
    def __init__(self):
        self.sells: List[Order] = []
        self.buys: List[Order] = []

    def add_order(self, order: Order) -> None:
        if order.side == Side.SELL:
            self.sells.append(order)
            self._sort(Side.SELL)
        else:
            self.buys.append(order)
            self._sort(Side.BUY)

    def update_order(self, order: Order) -> bool:
        for seq, side in ((self.sells, Side.SELL), (self.buys, Side.BUY)):
            for i, existing in enumerate(seq):
                if existing.id == order.id:
                    seq[i] = order
                    self._sort(side)
                    return True
        return False

    def remove_order(self, order_id: str) -> None:
        for seq in (self.sells, self.buys):
            for i, o in enumerate(seq):
                if o.id == order_id:
                    seq.pop(i)
                    return

    def get_best(self, side: Side) -> Optional[Order]:
        seq = self.sells if side == Side.SELL else self.buys
        return seq[0] if seq else None

    def delete_best(self, side: Side) -> Optional[Order]:
        seq = self.sells if side == Side.SELL else self.buys
        if not seq:
            return None
        return seq.pop(0)

    def get_by_side(self, side: Side) -> List[Order]:
        return list(self.sells if side == Side.SELL else self.buys)

    def _sort(self, side: Side) -> None:
        if side == Side.SELL:
            # (낮은 가격) -> (빠른 시간) -> (많은 수량)
            self.sells.sort(
                key=lambda o: (o.price, o.created_at.timestamp(), -o.quantity)
            )
        else:
            # (높은 가격) -> (빠른 시간) -> (많은 수량)
            self.buys.sort(
                key=lambda o: (-o.price, o.created_at.timestamp(), -o.quantity)
            )