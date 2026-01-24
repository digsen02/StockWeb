from flask import Flask
from flask_jwt_extended import JWTManager

from server.routes.auth_api import auth_bp
from server.routes.manage_api import manage_bp
from server.routes.trade_api import trade_bp
from server.routes.views import views

def create_app():
    app = Flask(__name__, template_folder="./static")

    # JWT 설정 (실제에선 환경변수로 빼기)

    app.config["JWT_SECRET_KEY"] = "dev-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_IDENTITY_CLAIM"] = "identity"

    JWTManager(app)

    app.register_blueprint(views)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(manage_bp)

    return app