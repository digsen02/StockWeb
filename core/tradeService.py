from decimal import Decimal
from domain.holding import Holding
from domain.portfolio import Portfolio
from domain.log import MatchLog
from domain.order import Side, Order
from repository.companyRepo import CompanyRepo
from repository.orderBookRepo import OrderBookRepo
from repository.matchLogRepo import MatchLogRepo
from repository.orderRepo import OrderRepo
from repository.portfolioRepo import PortfolioRepo


class TradeService:
    def __init__(
        self,
        order_repo : OrderRepo,
        order_book_repo: OrderBookRepo,
        match_log_repo: MatchLogRepo,
        portfolio_repo: PortfolioRepo,
        company_repo: CompanyRepo,
    ) -> None:
        self.order_repo = order_repo
        self.order_book_repo = order_book_repo
        self.match_log_repo = match_log_repo
        self.portfolio_repo = portfolio_repo
        self.company_repo = company_repo

    def _settle_trade(
        self,
        buyer_order: Order,
        seller_order: Order,
        trade_price: Decimal,
        trade_qty: int,
    ) -> None:

        buyer_pid = buyer_order.shareholder_id
        seller_pid = seller_order.shareholder_id
        company_id = buyer_order.company_id
        company = self.company_repo.get_by_id(company_id)
        company_name = company.name
        current_price = company.current_price

        total_cost = trade_price * trade_qty

        buyer_portfolio: Portfolio = self.portfolio_repo.get_by_shareholder_id(buyer_pid)
        seller_portfolio: Portfolio = self.portfolio_repo.get_by_shareholder_id(seller_pid)

        if buyer_portfolio is None or seller_portfolio is None:
            raise ValueError("포트폴리오 없음")

        if buyer_portfolio.cash_balance < total_cost:
            raise ValueError("매수자 현금 부족")

        buyer_portfolio.cash_balance -= total_cost

        buyer_holding = buyer_portfolio.get_holding(company_id)

        if buyer_holding is None:
            buyer_holding = Holding(
                company_id=company_id,
                portfolio_id=buyer_portfolio.id,
                name=company_name,
                quantity=trade_qty,
                avg_price=trade_price,
                current_price=current_price,
            )
        else:
            before_qty = buyer_holding.quantity
            before_cost = buyer_holding.avg_price * before_qty

            after_qty = before_qty + trade_qty
            after_cost = before_cost + total_cost

            buyer_holding.quantity = after_qty
            buyer_holding.avg_price = after_cost / after_qty
            buyer_holding.current_price = current_price

        buyer_portfolio.set_holding(buyer_holding)

        seller_portfolio.cash_balance += total_cost

        seller_holding = seller_portfolio.get_holding(company_id)

        seller_holding.quantity -= trade_qty

        if seller_holding.quantity == 0:
            seller_portfolio.holdings.pop(company_id, None)
            seller_portfolio.re_portfolio_value()
        else:
            seller_portfolio.set_holding(seller_holding)

        self.portfolio_repo.update(buyer_portfolio)
        self.portfolio_repo.update(seller_portfolio)

    # def _add_order(self, buy_order: Order, sell_order: Order):
    #     buyer_pid = buy_order.shareholder_id
    #     company_id = buy_order.company_id
    #
    #     self.order_repo.adds(
    #         Order(
    #             shareholder_id=buyer_pid,
    #             company_id=company_id,
    #             side=Side.BUY,
    #             quantity=trade_qty,
    #             price=trade_price,
    #         ),
    #         Order(
    #             shareholder_id=company_id,
    #             company_id=company_id,
    #             side=Side.SELL,
    #             quantity=trade_qty,
    #             price=trade_price,
    #         )
    #     )
    #
    #     self.match_log_repo.add(
    #         MatchLog(
    #             buy_order_id=buy_order.shareholder_id,
    #             sell_order_id=company_id,
    #             price=trade_price,
    #             quantity=trade_qty,
    #         )
    #     )

    def _buy_from_company(
        self,
        buy_order: Order,
    ) -> None:

        company_id = buy_order.company_id
        company = self.company_repo.get_by_id(company_id)
        if company is None:
            raise ValueError("회사 정보 없음")

        trade_price: Decimal = company.current_price  # 혹은 buy_order.price
        trade_qty: int = buy_order.quantity

        # 회사 잔여 주식 체크
        if company.remaining_shares < trade_qty:
            raise ValueError("회사 잔여 주식 부족")

        total_cost = trade_price * trade_qty

        buyer_pid = buy_order.shareholder_id
        buyer_portfolio: Portfolio = self.portfolio_repo.get_by_shareholder_id(buyer_pid)

        if buyer_portfolio is None:
            raise ValueError("매수자 포트폴리오 없음")

        if buyer_portfolio.cash_balance < total_cost:
            raise ValueError("매수자 현금 부족")

        buyer_portfolio.cash_balance -= total_cost

        buyer_holding = buyer_portfolio.get_holding(company_id)

        if buyer_holding is None:
            buyer_holding = Holding(
                company_id=company_id,
                portfolio_id=buyer_portfolio.id,
                name=company.name,
                quantity=trade_qty,
                avg_price=trade_price,
                current_price=company.current_price,
            )
        else:
            before_qty = buyer_holding.quantity
            before_cost = buyer_holding.avg_price * before_qty

            after_qty = before_qty + trade_qty
            after_cost = before_cost + total_cost

            buyer_holding.quantity = after_qty
            buyer_holding.avg_price = after_cost / after_qty
            buyer_holding.current_price = company.current_price

        buyer_portfolio.set_holding(buyer_holding)
        buyer_portfolio.re_portfolio_value()

        self.portfolio_repo.update(buyer_portfolio)

        company.remaining_shares -= trade_qty
        self.company_repo.update(company)

        self.order_repo.adds(
            Order(
                shareholder_id=buyer_pid,
                company_id=company_id,
                side=Side.BUY,
                quantity=trade_qty,
                price=trade_price,
            ),
            Order(
                shareholder_id=company_id,
                company_id=company_id,
                side=Side.SELL,
                quantity=trade_qty,
                price=trade_price,
            )
        )

        self.match_log_repo.add(
            MatchLog(
                buy_order_id=buy_order.shareholder_id,
                sell_order_id=company_id,
                price=trade_price,
                quantity=trade_qty,
            )
        )

    def match_orders(self, new_order: Order) -> bool:
        traded = False

        # ---------------- SELL 주문 -----------------
        if new_order.side == Side.SELL:
            while new_order.quantity > 0:
                best_buy = self.order_book_repo.get_best(Side.BUY)
                if best_buy is None:
                    break
                if new_order.price > best_buy.price:
                    break

                trade_price = best_buy.price
                trade_qty = min(new_order.quantity, best_buy.quantity)

                new_order.quantity -= trade_qty
                best_buy.quantity -= trade_qty
                traded = True

                self._settle_trade(
                    buyer_order=best_buy,
                    seller_order=new_order,
                    trade_price=trade_price,
                    trade_qty=trade_qty,
                )

                self.order_repo.adds(
                    Order(
                        shareholder_id=best_buy.shareholder_id,
                        company_id=best_buy.company_id,
                        side=Side.BUY,
                        quantity=trade_qty,
                        price=trade_price,
                    ),
                    Order(
                        shareholder_id=new_order.shareholder_id,
                        company_id=best_buy.company_id,
                        side=Side.SELL,
                        quantity=trade_qty,
                        price=trade_price,
                    )
                )

                self.match_log_repo.add(
                    MatchLog(
                        buy_order_id=best_buy.shareholder_id,
                        sell_order_id=new_order.shareholder_id,
                        price=trade_price,
                        quantity=trade_qty,
                    )
                )

                if best_buy.quantity == 0:
                    self.order_book_repo.delete_best(Side.BUY)
                else:
                    self.order_book_repo.update_by_id(best_buy)

            if new_order.quantity > 0:
                self.order_book_repo.add(new_order)

            return traded

        # ---------------- BUY 주문 -----------------
        else:
            while new_order.quantity > 0:
                best_sell = self.order_book_repo.get_best(Side.SELL)

                if best_sell is None:
                    self._buy_from_company(new_order)
                    traded = True
                    new_order.quantity = 0
                    break

                if best_sell.price > new_order.price:
                    break

                trade_price = best_sell.price
                trade_qty = min(new_order.quantity, best_sell.quantity)

                new_order.quantity -= trade_qty
                best_sell.quantity -= trade_qty
                traded = True

                self._settle_trade(
                    buyer_order=new_order,
                    seller_order=best_sell,
                    trade_price=trade_price,
                    trade_qty=trade_qty,
                )

                self.order_repo.adds(
                    Order(
                        shareholder_id=new_order.shareholder_id,
                        company_id=new_order.company_id,
                        side=Side.BUY,
                        quantity=trade_qty,
                        price=trade_price,
                    ),
                    Order(
                        shareholder_id=best_sell.shareholder_id,
                        company_id=new_order.company_id,
                        side=Side.SELL,
                        quantity=trade_qty,
                        price=trade_price,
                    )
                )

                self.match_log_repo.add(
                    MatchLog(
                        buy_order_id=new_order.shareholder_id,
                        sell_order_id=best_sell.shareholder_id,
                        price=trade_price,
                        quantity=trade_qty,
                    )
                )

                if best_sell.quantity == 0:
                    self.order_book_repo.delete_best(Side.SELL)
                else:
                    self.order_book_repo.update_by_id(best_sell)

            # 회사 물량으로 다 못 채웠거나, 호가 매칭 후에도 남은 경우에만 호가창에 올림
            if new_order.quantity > 0:
                self.order_book_repo.add(new_order)

            return traded