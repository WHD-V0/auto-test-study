"""学习用请求入口：显式状态校验、保守重试、最小日志和资源释放。"""
from __future__ import annotations

import logging
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.settings import settings

logger = logging.getLogger("api")


class APIError(Exception):
    """传输失败或非预期 HTTP 状态；不把响应正文写入异常。"""


class APIClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None,
                 max_retries: int | None = None):
        self.base_url = (base_url if base_url is not None else settings.base_url).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.timeout
        retries = max_retries if max_retries is not None else settings.max_retries
        if self.timeout <= 0 or retries < 0:
            raise ValueError("timeout 必须大于 0，max_retries 不能为负")
        self.session = requests.Session()
        retry = Retry(
            total=retries, status=retries,
            connect=0, read=0, redirect=0, other=0,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
            raise_on_status=False,
            respect_retry_after_header=False,
        )
        # 只重试指定状态；写请求、连接/读取异常都不自动重放。
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def set_token(self, token: str, scheme: str = "Bearer") -> None:
        self.session.headers["Authorization"] = f"{scheme} {token}"

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def request(self, method: str, path: str, expect_status: int | tuple[int, ...] = 200,
                **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        # 不记录 URL/query/body/headers/响应正文，避免教学代码泄漏凭据。
        logger.info(">>> %s", method.upper())
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.RequestException as exc:
            name = type(exc).__name__
            logger.error("请求失败: %s %s", method.upper(), name)
            # requests 原异常文本可能含 URL/query；不向报告附带它。
            raise APIError(f"网络错误: {name}") from None
        logger.info("<<< %s -> %s (%.0fms)", method.upper(), resp.status_code,
                    resp.elapsed.total_seconds() * 1000)
        statuses = (expect_status,) if isinstance(expect_status, int) else expect_status
        if resp.status_code not in statuses:
            raise APIError(f"状态码不符: 期望 {expect_status}, 实际 {resp.status_code}")
        return resp

    def get_json(self, path: str, expect_status: int = 200, **kwargs: Any) -> Any:
        return self.request("GET", path, expect_status, **kwargs).json()

    def post_json(self, path: str, body: dict, expect_status: int = 201, **kwargs: Any) -> Any:
        return self.request("POST", path, expect_status, json=body, **kwargs).json()

    def put_json(self, path: str, body: dict, expect_status: int = 200, **kwargs: Any) -> Any:
        return self.request("PUT", path, expect_status, json=body, **kwargs).json()

    def delete(self, path: str, expect_status: int | tuple[int, ...] = 200,
               **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, expect_status, **kwargs)
