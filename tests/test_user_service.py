"""中级测试示例 —— UserService 模块
学习要点：
  - fixture 的使用与组合
  - tmp_path 内置 fixture（临时文件）
  - 测试文件读写
"""
import pytest
from src.user_service import User, UserService


@pytest.fixture
def service():
    return UserService()


@pytest.fixture
def service_with_users(service):
    """预填充两个用户的 service"""
    service.add_user(User("张三", "zhangsan@example.com", 25))
    service.add_user(User("李四", "lisi@example.com", 30))
    return service


# ── 增删查 ────────────────────────────────────

class TestAddUser:
    def test_add_success(self, service):
        user = User("王五", "wangwu@example.com", 28)
        service.add_user(user)
        assert service.get_user("wangwu@example.com") is user

    def test_add_duplicate_raises(self, service_with_users):
        with pytest.raises(ValueError, match="已存在"):
            service_with_users.add_user(User("重复", "zhangsan@example.com", 20))


class TestGetUser:
    def test_existing_user(self, service_with_users):
        user = service_with_users.get_user("zhangsan@example.com")
        assert user is not None
        assert user.name == "张三"

    def test_nonexistent_user(self, service_with_users):
        assert service_with_users.get_user("nobody@example.com") is None


class TestRemoveUser:
    def test_remove_existing(self, service_with_users):
        assert service_with_users.remove_user("zhangsan@example.com") is True
        assert service_with_users.get_user("zhangsan@example.com") is None

    def test_remove_nonexistent(self, service_with_users):
        assert service_with_users.remove_user("nobody@example.com") is False


class TestListUsers:
    def test_list_count(self, service_with_users):
        assert len(service_with_users.list_users()) == 2


# ── 文件持久化 ─────────────────────────────────

class TestPersistence:
    def test_save_and_load(self, service_with_users, tmp_path):
        filepath = str(tmp_path / "users.json")

        # 保存
        service_with_users.save_to_file(filepath)

        # 新 service 加载
        new_service = UserService()
        new_service.load_from_file(filepath)

        assert len(new_service.list_users()) == 2
        assert new_service.get_user("zhangsan@example.com").name == "张三"


# ── 使用全局 fixture ──────────────────────────

def test_create_from_global_fixture(service, sample_user_data):
    """学习：conftest.py 中定义的全局 fixture 可以直接使用"""
    user = User.from_dict(sample_user_data)
    service.add_user(user)
    assert service.get_user(sample_user_data["email"]).name == "张三"
