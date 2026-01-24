# domain/portfolio.py
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict

from domain.common import new_id
from domain.holding import Holding


@dataclass
class Portfolio:
    shareholder_id: str # FK
    cash_balance: Decimal
    portfolio_value: Decimal
    holdings: Dict[str, Holding] = field(default_factory=dict)  # key: company_id
    id: str = field(default_factory=new_id)  # PK
    created_at: datetime = field(default_factory=datetime.utcnow)

    def re_portfolio_value(self) -> None:
        total_value = sum(h.market_value for h in self.holdings.values())
        self.portfolio_value = total_value + self.cash_balance

        for h in self.holdings.values():
            h.weight = float(h.market_value / self.portfolio_value) if self.portfolio_value > 0 else 0.0

    def get_holding(self, company_id: str) -> Holding | None:
        return self.holdings.get(company_id)

    def set_holding(self, holding: Holding) -> None:
        self.holdings[holding.company_id] = holding
        self.re_portfolio_value()
