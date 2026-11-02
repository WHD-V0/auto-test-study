"""企业级 API 客户端 —— 接口自动化框架的核心

对比 src/api_client.py（教学版）的升级点，都是企业项目的标配：
  1. 统一 request() 入口：日志、耗时统计、异常包装集中在一处
  2. 自动重试：用 urllib3 Retry 处理网络抖动 / 5xx，而不是测试里 try/except
  3. 鉴权支持：登录后 set_token()，之后所有请求自动携带
  4. 配置驱动：base_url / timeout / 重试次数来自 config/，代码里零硬编码
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from config.settings import settings

logger = logging.getLogger("api")


class APIError(Exception):
    """业务侧统一异常：网络层错误或非预期状态码都包成它抛出"""


class APIClient:
    """所有接口测试共用的 HTTP 客户端（通常通过 conftest fixture 注入）"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self.timeout = timeout or settings.timeout
        retries = max_retries if max_retries is not None else settings.max_retries

        self.session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=0.5,                     # 重试间隔：0.5s, 1s, 2s...
            status_forcelist=[500, 502, 503, 504],  # 这些状态码自动重试
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    # ── 鉴权 ────────────────────────────────────
    def set_token(self, token: str, scheme: str = "Bearer") -> None:
        """登录接口拿到 token 后调用一次，之后所有请求自动携带"""
        self.session.headers["Authorization"] = f"{scheme} {token}"

    # ── 统一请求入口 ─────────────────────────────
    def request(
        self,
        method: str,
        path: str,
        expect_status: int = 200,
        **kwargs: Any,
    ) -> requests.Response:
        """发送请求并做基础校验，返回原始 Response（由测试自行断言响应体）

        expect_status: 期望的状态码，不符时抛 APIError 并附带响应内容，方便定位
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)

        logger.info(">>> %s %s params=%s json=%s", method.upper(), url, kwargs.get("params"), kwargs.get("json"))
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.RequestException as e:
            logger.error("请求失败: %s %s -> %s", method, url, e)
            raise APIError(f"网络错误: {e}") from e

        logger.info("<<< %s %s -> %s (%.0fms)", method.upper(), url, resp.status_code, resp.elapsed.total_seconds() * 1000)

        if resp.status_code != expect_status:
            raise APIError(
                f"状态码不符: 期望 {expect_status}, 实际 {resp.status_code}\n响应: {resp.text[:500]}"
            )
        return resp

    def get_json(self, path: str, expect_status: int = 200, **kwargs: Any) -> Any:
        """最常用快捷方法：请求 + 解析 JSON 一步到位"""
        return self.request("GET", path, expect_status, **kwargs).json()

    def post_json(self, path: str, body: dict, expect_status: int = 201, **kwargs: Any) -> Any:
        return self.request("POST", path, expect_status, json=body, **kwargs).json()

    def put_json(self, path: str, body: dict, expect_status: int = 200, **kwargs: Any) -> Any:
        return self.request("PUT", path, expect_status, json=body, **kwargs).json()

    def delete(self, path: str, expect_status: int = 200, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, expect_status, **kwargs)
