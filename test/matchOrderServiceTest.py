from decimal import Decimal
from core.tradeService import TradeService
from domain.company import Company
from domain.order import Order, Side
from repository.matchLogRepo import InMemoryMatchLogRepo
from repository.orderBookRepo import InMemoryOrderBookRepo

order_book = InMemoryOrderBookRepo(Company("Hanbit Electronics", 23, 120_000_000, Decimal("18.50"), logo_src="/static/logos/hanbit.png"))
match_log_repo = InMemoryMatchLogRepo()

trade_service = TradeService(order_book, match_log_repo)

sellOrder1 = Order("S-001", Side.SELL,  50,  Decimal("18.70"))
sellOrder2 = Order("S-002", Side.SELL, 100,  Decimal("18.60"))
sellOrder3 = Order("S-003", Side.SELL,  25,  Decimal("18.50"))
sellOrder4 = Order("S-004", Side.SELL,  40,  Decimal("19.00"))
sellOrder5 = Order("S-005", Side.SELL, 100,  Decimal("20.00"))

# ---- BUY ORDERS ----
buyOrder1  = Order("B-001", Side.BUY,   30,  Decimal("18.65"))
buyOrder2  = Order("B-002", Side.BUY,   80,  Decimal("18.55"))
buyOrder3  = Order("B-003", Side.BUY,   25,  Decimal("18.50"))
buyOrder4  = Order("B-004", Side.BUY,  100,  Decimal("19.00"))
buyOrder5  = Order("B-005", Side.BUY,   10,  Decimal("17.80"))

trade_service.add_orders(sellOrder1, sellOrder2, sellOrder3, sellOrder4, sellOrder5, buyOrder1, buyOrder2, buyOrder3, buyOrder4, buyOrder5)