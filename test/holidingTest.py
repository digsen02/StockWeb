from decimal import Decimal
from domain.holding import Holding
from domain.portfolio import Portfolio

holding = Holding(
    "SAMSUNG",
    100,
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    Decimal("0.00"),
    0.0
)
portfolio = Portfolio(
    Decimal("0.00"),
    Decimal("0.00")
)
portfolio.holdings["SAM"] = holding

print(holding)
print(portfolio)


tsetList = [123, 2, 3, 4, 5, 6]
tsetList.sort()
print(tsetList)
