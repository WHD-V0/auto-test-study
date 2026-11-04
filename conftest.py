"""共享基础 fixture；可修改的 HTTP session 按用例创建并关闭。"""
from pathlib import Path

import pytest
import yaml

from core.api_client import APIClient


@pytest.fixture
def api_client():
    with APIClient() as client:
        yield client


@pytest.fixture(scope="session")
def test_data():
    path = Path(__file__).parent / "data" / "users.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def sample_user_data():
    return {"name": "张三", "email": "zhangsan@example.com", "age": 25}


@pytest.fixture
def temp_file(tmp_path):
    path = tmp_path / "test_data.txt"
    path.write_text("hello world", encoding="utf-8")
    return path
