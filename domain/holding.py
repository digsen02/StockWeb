from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from domain.common import new_id


@dataclass
class Holding:
    company_id: str                 # 어떤 회사 주식인지 FK
    portfolio_id: str               # 어떤 포트폴리오의 주식인지 FK
    name: str                       # 회사명
    quantity: int                   # 보유 주식 수
    avg_price: Decimal              # 평단가
    current_price: Decimal          # 현재가
    weight: float = 0.0             # 포트 내 비중
    id: str = field(default_factory = new_id) #PK

    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def market_value(self) -> Decimal:
        """평가 금액 = 현재가 * 수량"""
        return self.current_price * self.quantity

    @property
    def unrealized_pnl(self) -> Decimal:
        """평가 손익 = (현재가 - 평단가) * 수량"""
        return (self.current_price - self.avg_price) * self.quantity

    def buy(self, quantity: int, price: Decimal) -> None:
        """추가 매수 시 평단가/수량 조정."""
        if quantity <= 0:
            return
        total_cost_before = self.avg_price * self.quantity
        total_cost_after = total_cost_before + price * quantity
        self.quantity += quantity
        self.avg_price = total_cost_after / self.quantity

    def sell(self, quantity: int) -> None:
        """매도 시 수량 감소"""
        if quantity <= 0:
            return
        if quantity > self.quantity:
            raise ValueError("보유 수량보다 많이 팔 수 없습니다.")
        self.quantity -= quantity
