# domain/market.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

from domain.common import new_id
from domain.company import Company
from domain.shareholder import Shareholder


@dataclass
class Market:
    name: str
    id: str = field(default_factory=new_id)
    companies: Dict[str, Company] = field(default_factory=dict)     # key: ticker
    shareholders: Dict[str, Shareholder] = field(default_factory=dict)  # key: shareholder.id
    created_at : datetime = field(default_factory=datetime.now)

    def add_company(self, company: Company) -> None:
        ticker = company.get_ticker()
        if ticker in self.companies:
            raise ValueError("ticker already exists.")
        self.companies[ticker] = company

    def add_shareholder(self, shareholder: Shareholder) -> None:
        if shareholder.id in self.shareholders:
            raise ValueError("shareholder already exists.")
        self.shareholders[shareholder.id] = shareholder

    def get_company(self, name: str | None = None, ticker: str | None = None) -> Company | None:
        if ticker is not None:
            return self.companies.get(ticker)
        if name is not None:
            for c in self.companies.values():
                if c.name == name:
                    return c
        return None

    def get_shareholder(self, shareholder_id: str) -> Shareholder | None:
        return self.shareholders.get(shareholder_id)