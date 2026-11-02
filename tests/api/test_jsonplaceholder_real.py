"""真实接口测试 —— 以公共测试站 JSONPlaceholder 为靶场

学习要点（对应企业真实项目）：
  - 用 marker 区分"真实接口"用例，离线环境可整体跳过
  - Schema 校验响应结构，而不是逐字段写死
  - CRUD 全流程：接口之间有依赖（创建返回的 id 供后续用例使用）
  - 业务异常场景（404、参数过滤）

运行:  pytest tests/api/test_jsonplaceholder_real.py
跳过:  pytest -m "not real_api"
"""
import pytest

from core.validator import assert_schema

pytestmark = pytest.mark.real_api

# 响应结构 Schema —— 定义一次，多处复用
USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
    },
}

POST_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "body", "userId"],
    "properties": {
        "id": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
        "userId": {"type": "integer"},
    },
}


# ── 查询类接口 ──────────────────────────────────

class TestQuery:
    @pytest.mark.smoke
    def test_get_user_by_id(self, api_client):
        """基础查询：状态码 + Schema + 业务字段三重断言"""
        user = api_client.get_json("/users/1")

        assert_schema(user, USER_SCHEMA, "用户详情")
        assert user["id"] == 1
        assert "@" in user["email"]

    def test_get_user_list_and_filter(self, api_client):
        """列表查询 + 查询参数过滤"""
        users = api_client.get_json("/users")
        assert len(users) == 10
        assert_schema(users[0], USER_SCHEMA, "用户列表首元素")

        # 按 username 过滤（服务端支持的 query 参数）
        filtered = api_client.get_json("/users", params={"username": "Bret"})
        assert len(filtered) == 1
        assert filtered[0]["id"] == 1

    def test_get_not_exist_user_returns_404(self, api_client):
        """异常场景：查不存在的资源，显式期望 404 而不是让请求报错"""
        resp = api_client.request("GET", "/users/9999", expect_status=404)
        assert resp.text == "{}"


# ── CRUD 全流程 ─────────────────────────────────

class TestCrudFlow:
    """一个完整业务链路：创建 -> 查询 -> 修改 -> 删除

    学习要点 1：接口依赖（后一步用前一步返回的 id）
    学习要点 2：认清靶场特性 —— JSONPlaceholder 是"伪 REST"，
      POST 返回 201 + id=101，但资源并不持久化，GET /posts/101 是 404。
      真实项目接口不会这样，所以"查询/修改/删除"步骤对已有资源 /posts/1 操作。
      接口测试的第一课：写用例前先用 curl/Postman 摸清接口真实行为。
    """

    def test_full_crud(self, api_client):
        # 1. 创建（REST 惯例：创建成功返回 201）
        payload = {"title": "速成学习", "body": "接口自动化", "userId": 1}
        created = api_client.post_json("/posts", payload)
        assert_schema(created, POST_SCHEMA, "创建结果")
        assert created["title"] == "速成学习"  # 服务端应原样返回提交内容

        # 2. 查询（对已有资源，见上方说明）
        detail = api_client.get_json("/posts/1")
        assert_schema(detail, POST_SCHEMA, "帖子详情")

        # 3. 修改
        updated = api_client.put_json("/posts/1", {**payload, "title": "修改后"})
        assert updated["title"] == "修改后"

        # 4. 删除
        api_client.delete("/posts/1")
