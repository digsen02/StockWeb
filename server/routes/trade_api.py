# server/routes/trade_api.py
from decimal import Decimal
from typing import Dict

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from core.tradeService import TradeService
from domain.order import Order, Side
from domain.company import Company

from repository.companyRepo import DbCompanyRepo
from repository.shareholderRepo import DbShareholderRepo
from repository.orderRepo import DbOrderRepo
from repository.orderBookRepo import InMemoryOrderBookRepo
from repository.matchLogRepo import DbMatchLogRepo
from repository.portfolioRepo import DbPortfolioRepo

trade_bp = Blueprint("trade_api", __name__, url_prefix="/trade")

company_repo = DbCompanyRepo()
shareholder_repo = DbShareholderRepo()
match_log_repo = DbMatchLogRepo()
portfolio_repo = DbPortfolioRepo()
order_repo = DbOrderRepo()

# 거래용 Company 캐시 (회사별 order_book 유지용)
COMPANY_RUNTIME: Dict[str, Company] = {}


def _current_user_id() -> str:
    current = get_jwt_identity()
    return current["id"]


def _get_runtime_company(company_id: str) -> Company | None:
    company = COMPANY_RUNTIME.get(company_id)
    if company is not None:
        return company

    db_company = company_repo.get_by_id(company_id)
    if not db_company:
        return None

    COMPANY_RUNTIME[company_id] = db_company
    return db_company


def _serialize_orderbook(book_repo: InMemoryOrderBookRepo) -> dict:
    from domain.order import Side as S

    bids = [
        {
            "orderId": o.id,
            "shareholderId": o.shareholder_id,
            "price": str(o.price),
            "quantity": o.quantity,
        }
        for o in book_repo.get_by_side(S.BUY)
    ]
    asks = [
        {
            "orderId": o.id,
            "shareholderId": o.shareholder_id,
            "price": str(o.price),
            "quantity": o.quantity,
        }
        for o in book_repo.get_by_side(S.SELL)
    ]
    return {"bids": bids, "asks": asks}


@trade_bp.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    data = request.get_json() or {}
    user_id = _current_user_id()

    market_id = data.get("marketId")
    company_id = data.get("companyId")
    side_str = data.get("side")
    quantity = data.get("quantity")
    price = data.get("price")

    if not market_id or not company_id or not side_str:
        return jsonify({"message": "marketId, companyId, side는 필수입니다."}), 400
    if quantity is None or price is None:
        return jsonify({"message": "quantity, price는 필수입니다."}), 400

    try:
        quantity = int(quantity)
        price = Decimal(str(price))
    except Exception:
        return jsonify({"message": "quantity는 정수, price는 숫자여야 합니다."}), 400

    if quantity <= 0 or price <= 0:
        return jsonify({"message": "quantity와 price는 0보다 커야 합니다."}), 400

    side_str_up = str(side_str).upper()
    if side_str_up not in ("BUY", "SELL"):
        return jsonify({"message": "side는 BUY 또는 SELL 이어야 합니다."}), 400

    side = Side.BUY if side_str_up == "BUY" else Side.SELL

    company = _get_runtime_company(company_id)
    if not company or company.market_id != market_id:
        return jsonify({"message": "회사를 찾을 수 없습니다."}), 404

    shareholder = shareholder_repo.get_by_user_and_market(user_id, market_id)
    if not shareholder:
        return jsonify({"message": "해당 마켓에 참가한 사용자만 주문할 수 있습니다."}), 403

    new_order = Order(
        shareholder_id=shareholder.id,
        company_id=company.id,
        side=side,
        quantity=quantity,
        price=price,
    )

    book_repo = InMemoryOrderBookRepo(company)

    service = TradeService(
        order_repo=order_repo,
        order_book_repo=book_repo,
        match_log_repo=match_log_repo,
        portfolio_repo=portfolio_repo,
        company_repo=company_repo,
    )

    service.match_orders(new_order)

    saved = book_repo.get_by_id(new_order.id)
    remaining_qty = saved.quantity if saved else 0
    filled_qty = quantity - remaining_qty

    if remaining_qty == 0 and filled_qty > 0:
        status = "filled"
    elif remaining_qty > 0 and filled_qty > 0:
        status = "partial"
    else:
        status = "open"

    orderbook = _serialize_orderbook(book_repo)

    return jsonify({
        "message": "주문 접수 완료",
        "order": {
            "id": new_order.id,
            "status": status,
            "side": side.value,
            "quantity": quantity,
            "filledQuantity": filled_qty,
            "remainingQuantity": remaining_qty,
            "price": str(new_order.price),
        },
        "orderBook": orderbook,
    }), 201


@trade_bp.route("/orderbook", methods=["GET"])
@jwt_required()
def get_orderbook():
    market_id = request.args.get("marketId")
    company_id = request.args.get("companyId")

    if not market_id or not company_id:
        return jsonify({"message": "marketId, companyId는 필수입니다."}), 400

    company = _get_runtime_company(company_id)
    if not company or company.market_id != market_id:
        return jsonify({"message": "회사를 찾을 수 없습니다."}), 404

    book_repo = InMemoryOrderBookRepo(company)
    orderbook = _serialize_orderbook(book_repo)
    return jsonify(orderbook), 200
