import enum
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from domain.common import new_id

class ShareholderRole(str, enum.Enum):
    PARTICIPANT = "participant"
    ADMIN = "admin"

@dataclass
class Shareholder:
    user_id: str #FK
    market_id: str #FK
    cash_balance: Decimal
    portfolio_value: Decimal
    role: ShareholderRole
    id: str = field(default_factory=new_id) #PK
    created_at: datetime = field(default_factory=datetime.utcnow)