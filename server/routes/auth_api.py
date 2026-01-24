# server/routes/auth_api.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from core.authService import AuthService, AuthError
from repository.userRepo import DbUserRepo

auth_bp = Blueprint("auth_api", __name__, url_prefix="/auth")

user_repo = DbUserRepo()
auth_service = AuthService(user_repo)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    nickname = data.get("nickname")
    password = data.get("password")
    password_confirm = data.get("passwordConfirm")

    try:
        user = auth_service.register(email, nickname, password, password_confirm)
    except AuthError as e:
        return jsonify({"message": e.message}), e.status_code

    return jsonify({
        "message": "회원가입이 완료되었습니다.",
        "user": {
            "id": user.id,
            "email": user.email,
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    try:
        user = auth_service.login(email, password)
    except AuthError as e:
        return jsonify({"message": e.message}), e.status_code

    access_token = create_access_token(identity={"id": user.id, "email": user.email})

    return jsonify({
        "accessToken": access_token,
        "tokenType": "Bearer",
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current = get_jwt_identity()  # { "id": ..., "email": ... }
    user = user_repo.get_by_id(current["id"])
    return jsonify({
        "userId": current["id"],
        "email": current["email"],
        "userNickname": user.nickname,
    }), 200
