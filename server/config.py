from flask import app

class Config:

    app.config["JWT_SECRET_KEY"] = "dev-secret-key"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_IDENTITY_CLAIM"] = "identity"