from flask import Blueprint, render_template

views = Blueprint("views", __name__)

# 1. 홈
@views.route("/")
def home_page():
    return render_template("home.html")

# 2. 로그인
@views.route("/login")
def login_page():
    return render_template("login.html")

# 3. 회원가입
@views.route("/register")
def register_page():
    return render_template("register.html")

# 4. 마켓 생성 페이지
@views.route("/markets/new")
def market_make_page():
    return render_template("market_make.html")

# 5. 내가 참가한 마켓 목록
@views.route("/markets/me/page")
def my_markets_page():
    return render_template("my_markets.html")

# 6. 마켓 상세
@views.route("/markets/<market_id>")
def market_show_page(market_id):
    return render_template("market_show.html", market_id=market_id)

# 7. 내 포트폴리오
@views.route("/portfolio")
def portfolio_page():
    return render_template("portfolio.html")

# 8. 주식 거래 창
@views.route("/trade/<market_id>")
def trade_page(market_id):
    return render_template("trade.html", market_id=market_id)

# 9. 회사 생성 페이지
@views.route("/markets/<market_id>/companies/new")
def company_create_page(market_id):
    return render_template("market_company_create.html", market_id=market_id)