# models/user.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    email: str
    nome: Optional[str] = None
    role: str = "user"
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            email=data.get("email", ""),
            nome=data.get("nome"),
            role=data.get("role", "user"),
            created_at=data.get("created_at"),
        )
