"""数据驱动测试 —— 学习要点：同一逻辑用不同数据反复验证

两种主流做法本项目都演示了：
  1. parametrize + yaml 数据（数据在收集期加载，最常用）
  2. 循环内断言（同一个测试里遍历数据集，报告更紧凑）

数据文件: data/users.yaml —— 改数据不用改代码
"""
import pytest

from core.validator import assert_schema

pytestmark = pytest.mark.real_api

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "email"],
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
    },
}

# yaml 数据在收集期就要用（parametrize 的参数不能来自 fixture），
# 所以这里直接在模块级加载 —— 企业项目通常封装成 data_loader 工具
import yaml
with open("data/users.yaml", encoding="utf-8") as _f:
    _data = yaml.safe_load(_f)


# ── 方式一：parametrize，每条数据是一个独立用例 ────

class TestParametrizedUsers:
    """yaml 里加一条数据，这里就自动多一个用例，代码零改动"""

    @pytest.mark.parametrize("user_case", _data["users"], ids=[f"用户{u['id']}" for u in _data["users"]])
    def test_user_schema_and_name(self, api_client, user_case):
        user = api_client.get_json(f"/users/{user_case['id']}")

        assert_schema(user, USER_SCHEMA, f"用户{user_case['id']}")
        assert user_case["name_contains"] in user["name"]

    @pytest.mark.parametrize("post", _data["new_posts"], ids=[p["title"] for p in _data["new_posts"]])
    def test_create_post(self, api_client, post):
        created = api_client.post_json("/posts", {
            "title": post["title"],
            "body": post["body"],
            "userId": post["user_id"],
        })
        assert created["title"] == post["title"]
        assert created["userId"] == post["user_id"]


# ── 方式二：单用例内遍历数据（报告更紧凑） ──────────

class TestLoopUsers:
    def test_all_users_have_valid_schema(self, api_client, test_data):
        """一次请求列表，循环校验每条数据 —— 列表类接口的首选用例写法"""
        users = api_client.get_json("/users")

        assert len(users) >= len(test_data["users"]), "用户数少于数据文件预期"
        for user in users:
            assert_schema(user, USER_SCHEMA, f"用户{user['id']}")
