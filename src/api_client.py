"""API 客户端模块 —— 用于学习 mock 和进阶测试"""
from __future__ import annotations

import requests
from typing import Any, Optional, Dict


class APIClient:
    """封装 HTTP 请求的 API 客户端"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, path: str, params: Optional[Dict] = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, data: Optional[Dict] = None) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.post(url, json=data, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def upload_file(self, path: str, filepath: str) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        with open(filepath, "rb") as f:
            resp = self.session.post(url, files={"file": f}, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
