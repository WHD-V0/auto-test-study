"""全局 fixture，所有测试文件共享

学习要点：
  - scope="session" 的重量级资源（HTTP 客户端）整个测试进程只创建一次
  - 测试代码不直接 import 配置/客户端，而是通过 fixture 注入 —— 换环境只改一处
"""
import pytest
import yaml

from core.api_client import APIClient


# ── 接口测试全局 fixture ─────────────────────────

@pytest.fixture(scope="session")
def api_client():
    """企业级 API 客户端（连接配置读取 config/config.yaml）"""
    return APIClient()


@pytest.fixture(scope="session")
def test_data():
    """加载 data/ 下的测试数据（数据驱动用）"""
    path = "data/users.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── 单元测试阶段就有的 fixture ────────────────────

@pytest.fixture
def sample_user_data():
    """提供示例用户数据"""
    return {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25,
    }


@pytest.fixture
def temp_file(tmp_path):
    """在临时目录创建一个测试文件"""
    f = tmp_path / "test_data.txt"
    f.write_text("hello world", encoding="utf-8")
    return f
