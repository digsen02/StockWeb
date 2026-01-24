from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class User:
    id: str
    email: str
    nickname: str
    password_hash: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def new(email: str, nickname: str ,password_hash: str) -> "User":
        return User(
            id=str(uuid.uuid4()),
            email=email,
            nickname=nickname,
            password_hash=password_hash,
        )