from decimal import Decimal
from domain.company import Company
from domain.order import Order, Side
from repository.repositories import CompanyOrderBookRepo

order_book = CompanyOrderBookRepo(Company("Hanbit Electronics", 23, 120_000_000, Decimal("18.50"), logo_src="/static/logos/hanbit.png"))

sellOrder6 = Order("test_order_011", Side.SELL, 200, Decimal("0.75"))
sellOrder1 = Order("test_order_001", Side.SELL, 1,   Decimal("1000.00"))
buyOrder1  = Order("test_order_002", Side.BUY,  10,  Decimal("12.34"))
sellOrder2 = Order("test_order_003", Side.SELL, 50,  Decimal("13.10"))
buyOrder2  = Order("test_order_004", Side.BUY,  5,   Decimal("999.99"))
sellOrder3 = Order("test_order_005", Side.SELL, 200, Decimal("0.75"))
buyOrder3  = Order("test_order_006", Side.BUY,  1,   Decimal("345.67"))
sellOrder4 = Order("test_order_007", Side.SELL, 3,   Decimal("150.00"))
buyOrder4  = Order("test_order_008", Side.BUY,  25,  Decimal("1.23"))
sellOrder5 = Order("test_order_009", Side.SELL, 100, Decimal("8.90"))
buyOrder5  = Order("test_order_010", Side.BUY,  2,   Decimal("4500.00"))

order_book.adds()

print(order_book.delete_best(Side.SELL))
print(order_book.delete_best(Side.BUY))