"""responses 库离线接口测试 —— 不发真实网络请求，也能测"接口层"逻辑

为什么需要它：
  - 真实接口测试慢、依赖环境；日常开发中大部分接口用例应该离线跑
  - responses 在 requests 库层面伪造响应，比 unittest.mock 更贴近真实 HTTP
    （状态码、headers、json 序列化都是真实行为）

学习要点：
  - @responses.activate 装饰器 + responses.add 注册模拟响应
  - 校验"发出去的请求"是否正确（URL、query、body）
  - 模拟各种状态码/超时，覆盖异常分支
"""
import pytest
import responses

from config.settings import settings
from core.api_client import APIClient, APIError


@pytest.fixture
def client():
    """离线测试用自己的客户端实例，URL 来自同一份配置（不发请求，无网络开销）"""
    return APIClient(max_retries=0)


# ── 基础用法 ────────────────────────────────────

class TestResponsesBasics:
    @responses.activate
    def test_get_with_mocked_response(self, client):
        """注册一个模拟响应，然后像真实接口一样调用"""
        responses.add(
            responses.GET,
            f"{settings.base_url}/users/1",
            json={"id": 1, "name": "Leanne Graham", "email": "leanne@april.biz"},
            status=200,
        )

        user = client.get_json("/users/1")

        assert user["id"] == 1
        assert len(responses.calls) == 1
        # 校验"发出去的请求"拼装是否正确
        assert responses.calls[0].request.url.endswith("/users/1")

    @responses.activate
    def test_query_params_are_sent(self, client):
        responses.add(
            responses.GET,
            f"{settings.base_url}/users",
            json=[{"id": 1}],
            status=200,
        )

        client.get_json("/users", params={"page": 2, "size": 10})

        sent = responses.calls[0].request
        assert "page=2" in sent.url and "size=10" in sent.url

    @responses.activate
    def test_post_body_is_json_serialized(self, client):
        responses.add(responses.POST, f"{settings.base_url}/posts", json={"id": 101}, status=201)

        result = client.post_json("/posts", {"title": "t", "body": "b", "userId": 1})

        assert result["id"] == 101
        sent = responses.calls[0].request
        assert sent.headers["Content-Type"] == "application/json"
        assert b'"title": "t"' in sent.body or '"title":"t"' in sent.body


# ── 异常分支覆盖 ─────────────────────────────────

class TestErrorBranches:
    @responses.activate
    def test_status_mismatch_raises(self, client):
        """实际状态码与 expect_status 不符时抛 APIError"""
        responses.add(responses.GET, f"{settings.base_url}/broken", json={}, status=503)

        with pytest.raises(APIError, match="503"):
            client.get_json("/broken")

    @responses.activate
    def test_expect_non_200_on_purpose(self, client):
        """异常用例：主动期望 404，正常返回"""
        responses.add(responses.GET, f"{settings.base_url}/users/999", body="{}", status=404)

        resp = client.request("GET", "/users/999", expect_status=404)
        assert resp.status_code == 404

    @responses.activate
    def test_network_timeout_is_wrapped(self, client):
        """responses 可以模拟连接级异常（超时/拒绝连接）

        注意：要用 requests 的异常类型（它是 RequestException 子类），
        客户端才能统一包装成 APIError —— 这正是企业客户端封装的价值
        """
        import requests
        responses.add(
            responses.GET,
            f"{settings.base_url}/slow",
            body=requests.exceptions.ConnectTimeout("timed out"),
        )

        with pytest.raises(APIError, match="网络错误"):
            client.get_json("/slow")


# ── 进阶技巧 ────────────────────────────────────

class TestAdvanced:
    @responses.activate
    def test_same_url_different_responses(self, client):
        """同一个 URL 按注册顺序依次返回 —— 模拟"第一次查询/第二次已变更"类场景"""
        url = f"{settings.base_url}/stock"
        responses.add(responses.GET, url, json={"price": 100})
        responses.add(responses.GET, url, json={"price": 105})

        assert client.get_json("/stock")["price"] == 100
        assert client.get_json("/stock")["price"] == 105

    @responses.activate
    def test_token_header_propagates(self, client):
        """验证鉴权：set_token 之后请求头确实带了 Authorization"""
        responses.add(responses.GET, f"{settings.base_url}/me", json={"ok": True})

        client.set_token("fake-jwt-token")
        client.get_json("/me")

        auth = responses.calls[0].request.headers["Authorization"]
        assert auth == "Bearer fake-jwt-token"
