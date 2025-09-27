from datetime import datetime

class Company :
    def __init__(self, name, age, issued_shares, issued_price, logo_src = None, ticker = None):
        self.name = name

        if ticker is not None:
            self._ticker = ticker.upper()
        else :
            name_replaced = name.replace(" ", "")
            if len(name_replaced) <= 4:
                self._ticker = name_replaced
            else :
                self._ticker = name_replaced[:len(name_replaced):len(name_replaced)//4 + 1].upper()
        self.age = age
        self.logo_src = logo_src
        self._issued_shares = issued_shares #발행 주
        self._issued_price = issued_price #발행가
        self._par_value = None #액면가
        self.current_price = issued_price # 현재가

        self.order_book_sell = [] #{id, 주, 가격, 시간}
        self.order_book_buy = [] #{id, 주, 가격, 시간}

    def get_ticker(self):
        return self._ticker

    def get_issued_shares(self):
        return self._issued_shares

    def set_current_price(self, current_price):
        self.current_price = current_price

    def match_orders(self):
        if not self.order_book_sell or not self.order_book_buy:
            return None

        buy_order = self.order_book_buy[0]
        sell_order = self.order_book_sell[0]

        if buy_order["price"] == sell_order["price"] and buy_order["quantity"] == sell_order["quantity"]:
            self.current_price = sell_order["price"]
            self.order_book_buy.pop(0)
            self.order_book_sell.pop(0)
            return True
        return False

    def remove_order_sell(self, order_id):
        self.order_book_sell.pop(order_id)

    def remove_order_buy(self, order_id):
        self.order_book_buy.pop(order_id)

    def show_order(self, is_sell = False):
        for order_book in (self.order_book_sell if is_sell else  self.order_book_buy):
            print(order_book)

class FinancialStatements : #재무제표
    pass


class Market :
    def __init__(self, name : str):
        self.name = name
        self.companies = {}
        self.shareholders = {}

    def add_company(self, _company: Company):
        if _company.get_ticker() not in self.companies:
            self.companies[_company.get_ticker()] = _company
        else :
            raise Exception("ticker already exists.")

    def add_shareholder(self, _shareholder):
        if _shareholder.id not in self.shareholders:
            self.shareholders[_shareholder.id] = _shareholder
        else:
            raise Exception("shareholders already exists.")

    def get_company(self, name = None, ticker = None):
        if ticker:
            return self.companies.get(ticker)
        elif name:
            for company in self.companies.values():
                if company.name == name:
                    return company
        return None

    def show_companies(self):
        for _company in self.companies.values():
            print(_company.name)
            print(_company.get_ticker())
            print(_company.get_issued_shares())

    def get_shareholder(self, id):
        for _shareholder in self.shareholders.values():
            if _shareholder.id == id:
                return _shareholder
        return None

    def add_order_sell(self, id, ticker, quantity, price):
        """매도 주문"""
        shareholder = self.get_shareholder(id)
        if shareholder is None:
            raise Exception("존재하지 않는 주주입니다.")

        company = self.get_company(ticker=ticker)
        if company is None:
            raise Exception("존재하지 않는 회사입니다.")

        company.order_book_sell.append({
            "id": id,
            "order_id": f"{id}_{quantity}_{price}_{datetime.now()}",
            "quantity": quantity,
            "price": price,
            "time": datetime.now()
        })
        # 시간 내림차순, 가격 오름차순
        # 살려는 가격이 높으면 높을수록 먼저 거래함.
        company.order_book_sell.sort(
            key=lambda order_book: (-order_book["time"].timestamp(), order_book["price"], order_book["quantity"]))

        if company.match_orders() :
            pass #여기에 remove 넣어야함

    def add_order_buy(self, id, ticker, quantity, price):
        """매수 주문"""
        shareholder = self.get_shareholder(id)
        if shareholder is None:
            raise Exception("존재하지 않는 주주입니다.")

        company = self.get_company(ticker=ticker)
        if company is None:
            raise Exception("존재하지 않는 회사입니다.")

        company.order_book_buy.append({
            "id": id,
            "order_id": f"{id}_{quantity}_{price}_{datetime.now()}",
            "quantity": quantity,
            "price": price,
            "time": datetime.now()
        })
        # 시간 내림차순, 가격 내림차순
        # 팔려는 가격이 낮으면 낮을수록 먼저 거래함.
        company.order_book_buy.sort(
            key=lambda order_book: (-order_book["time"].timestamp(), -order_book["price"], order_book["quantity"]))

        if company.match_orders() :
            shareholder.portfolio.add_holding(company, quantity, price)