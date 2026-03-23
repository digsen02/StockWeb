import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from server.routes.auth_api import auth_bp
from server.routes.manage_api import manage_bp
from server.routes.trade_api import trade_bp
from server.routes.views import views

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder="./static")

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_TYPE"] = os.getenv("JWT_HEADER_TYPE", "Bearer")
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_IDENTITY_CLAIM"] = os.getenv("JWT_IDENTITY_CLAIM", "identity")

    JWTManager(app)
    app.register_blueprint(views)
    app.register_blueprint(auth_bp)
    app.register_blueprint(trade_bp)
    app.register_blueprint(manage_bp)


    return app
