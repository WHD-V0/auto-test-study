"""用户服务模块 —— 用于学习 fixture 和中等复杂度测试"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, List


class User:
    def __init__(self, name: str, email: str, age: int):
        self.name = name
        self.email = email
        self.age = age

    def to_dict(self) -> dict:
        return {"name": self.name, "email": self.email, "age": self.age}

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(name=data["name"], email=data["email"], age=data["age"])


class UserService:
    """用户管理服务，支持增删查和文件持久化"""

    def __init__(self):
        self._users: Dict[str, User] = {}

    def add_user(self, user: User) -> None:
        if user.email in self._users:
            raise ValueError(f"用户 {user.email} 已存在")
        self._users[user.email] = user

    def get_user(self, email: str) -> Optional[User]:
        return self._users.get(email)

    def remove_user(self, email: str) -> bool:
        if email in self._users:
            del self._users[email]
            return True
        return False

    def list_users(self) -> List[User]:
        return list(self._users.values())

    def save_to_file(self, filepath: str) -> None:
        data = [u.to_dict() for u in self._users.values()]
        Path(filepath).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_from_file(self, filepath: str) -> None:
        raw = Path(filepath).read_text(encoding="utf-8")
        data = json.loads(raw)
        self._users.clear()
        for item in data:
            user = User.from_dict(item)
            self._users[user.email] = user
