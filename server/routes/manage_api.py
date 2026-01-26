# server/routes/manage_api.py
from decimal import Decimal

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from domain.market import Market
from domain.shareholder import Shareholder, ShareholderRole
from domain.portfolio import Portfolio
from domain.company import Company
from repository.companyRepo import DbCompanyRepo

from repository.marketRepo import DbMarketRepo
from repository.shareholderRepo import DbShareholderRepo
from repository.portfolioRepo import DbPortfolioRepo
from repository.userRepo import DbUserRepo

manage_bp = Blueprint("manage_api", __name__, url_prefix="/manage")

market_repo = DbMarketRepo()
shareholder_repo = DbShareholderRepo()
portfolio_repo = DbPortfolioRepo()
company_repo = DbCompanyRepo()
user_repo = DbUserRepo()


def _current_user_id() -> str:
    current = get_jwt_identity()
    return current["id"]


@manage_bp.route("/markets", methods=["GET"])
@jwt_required()
def list_markets():
    markets = market_repo.list_all()
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
        }
        for m in markets
    ]), 200


@manage_bp.route("/markets/me", methods=["GET"])
@jwt_required()
def my_markets():
    user_id = _current_user_id()
    shareholders = shareholder_repo.get_by_user_id(user_id)  # List[Shareholder]

    result = []
    for sh in shareholders:
        market = market_repo.get_by_id(sh.market_id)
        if not market:
            continue

        portfolio = portfolio_repo.get_by_shareholder_id(sh.id)
        cash = None
        total = None
        if portfolio:
            cash = portfolio.cash_balance
            total = portfolio.portfolio_value
        else:
            cash = sh.cash_balance
            total = sh.portfolio_value

        result.append({
            "market": {
                "id": market.id,
                "name": market.name,
            },
            "shareholder": {
                "cashBalance": str(cash),
                "portfolioValue": str(total),
            }
        })

    return jsonify(result), 200


@manage_bp.route("/markets", methods=["POST"])
@jwt_required()
def create_market():
    user_id = _current_user_id()
    data = request.get_json() or {}
    name = data.get("name")

    if not name:
        return jsonify({"message": "마켓 이름을 입력해주세요."}), 400

    market = Market(name=name)
    market_repo.add(market)

    initial_cash = Decimal("1000000")
    shareholder = Shareholder(
        user_id=user_id,
        market_id=market.id,
        cash_balance=initial_cash,
        portfolio_value=initial_cash,
        role=ShareholderRole.ADMIN
    )
    shareholder_repo.add(shareholder)

    portfolio = Portfolio(
        shareholder_id=shareholder.id,
        cash_balance=initial_cash,
        portfolio_value=initial_cash,
    )
    portfolio_repo.add(portfolio)

    return jsonify({
        "message": "마켓 생성 및 참가 완료",
        "market": {
            "id": market.id,
            "name": market.name,
        }
    }), 201


@manage_bp.route("/markets/join", methods=["POST"])
@jwt_required()
def join_market():
    user_id = _current_user_id()
    data = request.get_json() or {}
    market_id = data.get("marketId")

    if not market_id:
        return jsonify({"message": "marketId 가 필요합니다."}), 400

    market = market_repo.get_by_id(market_id)
    if not market:
        return jsonify({"message": "해당 마켓을 찾을 수 없습니다."}), 404

    # 이미 참가했는지 확인
    existing = shareholder_repo.get_by_user_and_market(user_id, market_id)
    if existing:
        return jsonify({"message": "이미 참가한 마켓입니다."}), 400

    initial_cash = Decimal("1000000")
    shareholder = Shareholder(
        user_id=user_id,
        market_id=market.id,
        cash_balance=initial_cash,
        portfolio_value=initial_cash,
        role=ShareholderRole.PARTICIPANT
    )
    shareholder_repo.add(shareholder)

    portfolio = Portfolio(
        shareholder_id=shareholder.id,
        cash_balance=initial_cash,
        portfolio_value=initial_cash,
    )
    portfolio_repo.add(portfolio)

    return jsonify({
        "message": "마켓 참가 완료",
        "market": {
            "id": market.id,
            "name": market.name,
        }
    }), 200


@manage_bp.route("/markets/<market_id>", methods=["GET"])
@jwt_required()
def market_detail(market_id: str):
    market = market_repo.get_by_id(market_id)
    if not market:
        return jsonify({"message": "마켓을 찾을 수 없습니다."}), 404

    participants = shareholder_repo.list_all()
    participants = [sh for sh in participants if sh.market_id == market_id]

    result_participants = []
    for sh in participants:
        portfolio = portfolio_repo.get_by_shareholder_id(sh.id)
        user = user_repo.get_by_id(sh.user_id)

        if portfolio:
            cash = portfolio.cash_balance
            total = portfolio.portfolio_value
        else:
            cash = sh.cash_balance
            total = sh.portfolio_value

        result_participants.append({
            "shareholderId": sh.id,
            "userNickname": user.nickname,
            "cashBalance": str(cash),
            "portfolioValue": str(total),
        })

    companies = company_repo.list_all()
    companies = [c for c in companies if c.market_id == market_id]

    companies_json = []
    for c in companies:
        change = c.current_price - c.issued_price
        change_percent = (change / c.issued_price * 100) if c.issued_price != 0 else Decimal("0")
        companies_json.append({
            "id": c.id,
            "name": c.name,
            "ticker": c.ticker,
            "currentPrice": str(c.current_price),
            "issuedPrice": str(c.issued_price),
            "change": str(round(change, 2)),
            "changePercent": float(round(change_percent, 2)),
        })

    current_user_id = _current_user_id()
    sh_me = shareholder_repo.get_by_user_and_market(current_user_id, market_id)
    is_admin = False
    if sh_me and getattr(sh_me, "role", None) is not None:
        is_admin = (sh_me.role == ShareholderRole.ADMIN)

    return jsonify({
        "id": market.id,
        "name": market.name,
        "participants": result_participants,
        "companies": companies_json,
        "isAdmin": is_admin,
    }), 200


@manage_bp.route("/markets/<market_id>/companies", methods=["POST"])
@jwt_required()
def create_company(market_id: str):
    current = get_jwt_identity()
    user_id = current["id"]

    market = market_repo.get_by_id(market_id)
    if not market:
        return jsonify({"message": "해당 마켓을 찾을 수 없습니다."}), 404

    data = request.get_json() or {}
    name = data.get("name")
    age = data.get("age")
    issued_shares = data.get("issuedShares")
    issued_price = data.get("issuedPrice")
    logo_src = data.get("logoSrc")
    ticker = data.get("ticker")
    par_value = data.get("parValue")

    if not name or age is None or issued_shares is None or issued_price is None:
        return jsonify({"message": "name, age, issuedShares, issuedPrice 는 필수입니다."}), 400

    try:
        age = int(age)
        issued_shares = int(issued_shares)
        issued_price = Decimal(str(issued_price))
        par_value_dec = Decimal(str(par_value)) if par_value is not None else None
    except Exception:
        return jsonify({"message": "age/issuedShares 는 정수, issuedPrice/parValue 는 숫자여야 합니다."}), 400

    company = Company(
        market_id=market_id,
        name=name,
        age=age,
        issued_shares=issued_shares,
        issued_price=issued_price,
        logo_src=logo_src,
        ticker=ticker,
        par_value=par_value_dec,
        remaining_shares=issued_shares,
    )

    company_repo.add(company)

    return jsonify({
        "message": "회사 생성 완료",
        "company": {
            "id": company.id,
            "marketId": company.market_id,
            "name": company.name,
            "ticker": company.ticker,
            "age": company.age,
            "issuedShares": company.issued_shares,
            "issuedPrice": str(company.issued_price),
            "currentPrice": str(company.current_price),
            "logoSrc": company.logo_src,
            "parValue": str(company.par_value) if company.par_value is not None else None,
        }
    }), 201

@manage_bp.route("/markets/<market_id>/companies/<company_id>", methods=["GET"])
@jwt_required()
def company_detail(market_id: str, company_id: str):
    company = company_repo.get_by_id(company_id)

    if not company:
        return jsonify({
            "message": "회사를 찾을 수 없습니다.",
            "debug": {
                "reason": "company_not_found",
                "market_id_in_url": market_id,
                "company_id_in_url": company_id,
            }
        }), 404

    if company.market_id != market_id:
        return jsonify({
            "message": "회사를 찾을 수 없습니다.",
            "debug": {
                "reason": "market_id_mismatch",
                "market_id_in_url": market_id,
                "market_id_in_company": company.market_id,
                "company_id_in_url": company_id,
            }
        }), 404

    change = company.current_price - company.issued_price
    change_rate = (change / company.issued_price * 100) if company.issued_price != 0 else Decimal("0")
    market_cap = company.issued_shares * company.current_price

    return jsonify({
        "id": company.id,
        "name": company.name,
        "ticker": company.ticker,
        "currentPrice": str(company.current_price),
        "issuedPrice": str(company.issued_price),
        "marketCap": int(market_cap),
        "changeRate": float(round(change_rate, 2)),
    }), 200