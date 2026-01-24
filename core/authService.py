from dataclasses import dataclass
from typing import Optional

from werkzeug.security import generate_password_hash, check_password_hash

from domain.user import User
from repository.userRepo import UserRepo

class AuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

@dataclass
class AuthService:
    user_repo: UserRepo

    def register(self, email: str, nickname: str, password: str, password_confirm: str) -> User:
        if not email or not password or not password_confirm:
            raise AuthError("email, password, passwordConfirm 모두 필요합니다.", 400)

        if password != password_confirm:
            raise AuthError("비밀번호와 비밀번호 확인이 일치하지 않습니다.", 400)

        if len(password) < 6:
            raise AuthError("비밀번호는 최소 6자 이상이어야 합니다.", 400)

        if self.user_repo.get_by_email(email) is not None:
            raise AuthError("이미 사용 중인 이메일입니다.", 409)

        password_hash = generate_password_hash(password)
        user = User.new(email=email, nickname=nickname ,password_hash=password_hash)
        self.user_repo.add(user)

        return user

    def login(self, email: str, password: str) -> User:
        if not email or not password:
            raise AuthError("email, password 모두 필요합니다.", 400)

        user: Optional[User] = self.user_repo.get_by_email(email)
        if user is None:
            raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다.", 401)

        if not check_password_hash(user.password_hash, password):
            raise AuthError("이메일 또는 비밀번호가 올바르지 않습니다.", 401)

        return user
