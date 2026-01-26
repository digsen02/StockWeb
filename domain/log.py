# domain/log.py
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain.common import new_id


@dataclass(kw_only=True)
class Log:
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class MatchLog(Log):
    buy_order_id: str
    sell_order_id: Optional[str]
    price: Decimal
    quantity: int
