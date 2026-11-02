"""进阶测试示例 —— APIClient 模块
学习要点：
  - unittest.mock.patch 模拟外部依赖（无需 pytest-mock）
  - MagicMock / PropertyMock 的用法
  - 测试异常场景
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from requests.exceptions import HTTPError

from src.api_client import APIClient


@pytest.fixture
def client():
    return APIClient("https://api.example.com")


# ── 使用 unittest.mock.patch ────────────────────

class TestGet:
    def test_get_success(self, client):
        """学习：用 patch.object 模拟 session.get"""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": 1, "name": "张三"}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            result = client.get("/users/1")

            assert result == {"id": 1, "name": "张三"}
            mock_get.assert_called_once_with(
                "https://api.example.com/users/1",
                params=None,
                timeout=10,
            )

    def test_get_with_params(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = [{"id": 1}]
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            result = client.get("/users", params={"page": 1})

            assert result == [{"id": 1}]
            mock_get.assert_called_once()
            # 验证传入了正确的 params
            call_kwargs = mock_get.call_args
            assert call_kwargs[1]["params"] == {"page": 1}


class TestPost:
    def test_post_success(self, client):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": 2, "created": True}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "post", return_value=mock_resp) as mock_post:
            data = {"name": "李四", "email": "lisi@example.com"}
            result = client.post("/users", data=data)

            assert result["created"] is True
            mock_post.assert_called_once()
            # 验证 json=data 被正确传递
            call_kwargs = mock_post.call_args
            assert call_kwargs[1]["json"] == data


class TestUploadFile:
    def test_upload_success(self, client, tmp_path):
        """学习：结合 tmp_path fixture 测试文件上传"""
        # 创建临时测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"filename": "test.txt", "uploaded": True}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "post", return_value=mock_resp) as mock_post:
            result = client.upload_file("/upload", str(test_file))

            assert result["uploaded"] is True
            mock_post.assert_called_once()


# ── 使用 @patch 装饰器 ──────────────────────────

class TestPatchDecorator:
    @patch("src.api_client.requests.Session")
    def test_session_creation(self, mock_session_cls):
        """学习：用 @patch 装饰器在类/模块级别模拟"""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        client = APIClient("https://api.example.com")
        assert client.session is mock_session


# ── 测试异常场景 ───────────────────────────────

class TestErrorHandling:
    def test_get_http_error(self, client):
        """学习：模拟请求返回 HTTP 错误"""
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = HTTPError("404 Not Found")

        with patch.object(client.session, "get", return_value=mock_resp):
            with pytest.raises(HTTPError, match="404"):
                client.get("/not-found")

    def test_post_server_error(self, client):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = HTTPError("500 Internal Server Error")

        with patch.object(client.session, "post", return_value=mock_resp):
            with pytest.raises(HTTPError, match="500"):
                client.post("/broken", data={})

    def test_get_timeout(self, client):
        """学习：模拟超时异常"""
        import requests
        with patch.object(client.session, "get", side_effect=requests.Timeout("连接超时")):
            with pytest.raises(requests.Timeout):
                client.get("/slow-endpoint")

    def test_get_connection_error(self, client):
        """学习：模拟连接错误"""
        import requests
        with patch.object(client.session, "get", side_effect=requests.ConnectionError("连接被拒绝")):
            with pytest.raises(requests.ConnectionError):
                client.get("/unreachable")


# ── Mock 进阶技巧 ──────────────────────────────

class TestMockTechniques:
    def test_verify_call_count(self, client):
        """学习：验证调用次数"""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_resp) as mock_get:
            client.get("/a")
            client.get("/b")
            client.get("/c")

            assert mock_get.call_count == 3

    def test_multiple_return_values(self, client):
        """学习：模拟多次调用返回不同结果"""
        resp1 = MagicMock()
        resp1.json.return_value = {"page": 1}
        resp1.raise_for_status.return_value = None

        resp2 = MagicMock()
        resp2.json.return_value = {"page": 2}
        resp2.raise_for_status.return_value = None

        with patch.object(client.session, "get", side_effect=[resp1, resp2]):
            r1 = client.get("/data")
            r2 = client.get("/data")

            assert r1 == {"page": 1}
            assert r2 == {"page": 2}

    def test_spy_pattern(self, client):
        """学习：Spy 模式 —— 观察真实行为同时保留 mock 能力"""
        # wraps 允许真实方法执行，同时记录调用
        mock_session = MagicMock(wraps=client.session)
        client.session = mock_session

        # 这里我们仍然 mock 了返回值以避免真实网络请求
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"ok": True}
        mock_resp.raise_for_status.return_value = None
        mock_session.get.return_value = mock_resp

        result = client.get("/health")
        assert result == {"ok": True}
        mock_session.get.assert_called_once()
