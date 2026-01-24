from Company import Company, Market

class Shareholder:
    def __init__(self, id):
        self.id = id
        self.portfolio = Portfolio()
        self.tendency = Tendency(self.portfolio)

    def buy_stock(self, market: Market, quantity: int, price=None, ticker=None, name=None):
        def buy(_price):
            if self.portfolio.get_cash() < _price * quantity:
                print("Buy stock failed : short of money")
            else:
                market.add_order_buy(self.id, company.get_ticker(), quantity, _price)

        if ticker:
            company = market.get_company(ticker=ticker)
        elif name:
            company = market.get_company(name=name)
        elif not name or not ticker:
            print("you must input a ticker or name")

        if not price is None:
            buy(price)
        else:
            buy(company.current_price)

    def sell_stock(self, market: Market, quantity: int, price=None, ticker=None, name=None):
        def sell(_price):
            print(self.portfolio.holdings)

            if self.portfolio.holdings[company.get_ticker()]["shares"] < quantity:
                print("Sell stock failed : short of shares")
            else:
                self.portfolio.add_holding(company, quantity)  # 바꿔야함

        if ticker:
            company = market.get_company(ticker=ticker)
        elif name:
            company = market.get_company(name=name)
        elif not name or not ticker:
            print("you must input a ticker or name")

        if not price is None:
            sell(price)
        else:
            sell(company.current_price)


class Tendency:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.stability = {}

    def get_stability(self):
        return self.stability

    def set_stability(self, stability):
        self.stability = stability


class Portfolio:
    def __init__(self):
        self.cash_balance = 0
        self.portfolio_value = 0
        self.holdings = {
            "ABC": {
                "name": "ABC Corp",
                "shares": 100,
                "avg_price": 10000,
                "current_price": 12000,
                "market_value": 1200000,
                "unrealized_pnl": 200000,
                "weight": 0.80
            }
        }

    def set_cash(self, cash):
        self.cash_balance = cash

    def get_cash(self):
        return self.cash_balance

    def add_holding(self, company: Company, quantity, price=None):
        def add(_price):
            if company.get_ticker() in self.holdings:
                holding = self.holdings[company.get_ticker()]
                new_avg_price = (holding["avg_price"] * holding["shares"] + _price * quantity) / (quantity + holding["shares"])
                # 주식 추가
                self.holdings[company.get_ticker()] = \
                    {
                        "name": company.name,
                        "shares": holding["shares"] + quantity,  # 보유 주식
                        "avg_price": new_avg_price,  # 매수 평균 단가
                        "current_price": company.current_price,  # 현재 가격
                        "market_value": (holding["shares"] + quantity) * company.current_price,  # 평가 금액
                        "unrealized_pnl": (company.current_price - new_avg_price) * (holding["shares"] + quantity), # 평가 손익
                        "weight": 0  # 비중
                    }
            else:
                self.holdings[company.get_ticker()] = \
                    {
                        "name": company.name,
                        "shares": quantity,
                        "avg_price": company.current_price,
                        "current_price": company.current_price,
                        "market_value": quantity * company.current_price,
                        "unrealized_pnl": 0,  # 현재 시점에서는 0
                        "weight": 0  # 구현 전
                    }

        if price is None:
            add(company.current_price)
        else:
            add(price)

    def remove_holding(self, company: Company, quantity, price=None):
        if company.get_ticker() not in self.holdings:
            raise Exception("you don't have this holding")

        holding = self.holdings[company.get_ticker()]

        if holding["shares"] < quantity:
            raise Exception("not enough shares to sell")

        remaining_shares = holding["shares"] - quantity

        if remaining_shares > 0:
            self.holdings[company.get_ticker()] = {
                "name": company.name,
                "shares": remaining_shares,
                "avg_price": holding["avg_price"],
                "current_price": company.current_price,
                "market_value": remaining_shares * company.current_price,
                "unrealized_pnl": (company.current_price - holding["avg_price"]) * remaining_shares,
                "weight": 0
            }
        else:
            self.holdings.pop(company.get_ticker())

    def __str__(self):
        return str(self.holdings)