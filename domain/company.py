from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from domain.order import OrderBook
from domain.common import new_id

@dataclass
class Company:
    market_id: str  # FK

    name: str
    age: int
    issued_shares: int              # 발행 주식 수
    issued_price: Decimal           # 발행가
    remaining_shares: int           # 회사가 들고 있는 남은 주식 수 (트레저리 주식)
    logo_src: Optional[str] = None
    ticker: Optional[str] = None
    par_value: Optional[Decimal] = None  # 액면가
    current_price: Decimal = None        # 현재가 (기본은 발행가)
    id: str = field(default_factory=new_id)  # PK

    created_at: datetime = field(default_factory=datetime.utcnow)

    # 회사별 주문 장
    order_book: OrderBook = field(default_factory=OrderBook, repr=False)

    def __post_init__(self):
        # ticker 생성
        if self.ticker is None:
            name_replaced = self.name.replace(" ", "")
            if len(name_replaced) <= 4:
                self.ticker = name_replaced.upper()
            else:
                step = len(name_replaced) // 4 + 1
                self.ticker = name_replaced[:len(name_replaced):step].upper()

        if self.current_price is None:
            self.current_price = self.issued_price

        if self.remaining_shares is None:
            self.remaining_shares = self.issued_shares

    def get_ticker(self) -> str:
        return self.ticker

    def change_price(self, new_price: Decimal) -> None:
        self.current_price = new_price
