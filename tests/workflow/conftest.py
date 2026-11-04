"""每个 worker 独立服务/数据库；每个用例独立客户端及资源回收。"""
from threading import Thread
from uuid import uuid4

import pytest

from core.api_client import APIClient
from sandbox.task_api import create_server


@pytest.fixture(scope="session")
def local_api_db(tmp_path_factory):
    return tmp_path_factory.mktemp("task-api") / "tasks.sqlite3"


@pytest.fixture(scope="session")
def local_api_url(local_api_db):
    server = create_server(local_api_db)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


@pytest.fixture
def anonymous_client(local_api_url):
    with APIClient(local_api_url, timeout=3, max_retries=0) as client:
        # 本机靶场不经系统代理；真实环境按团队代理配置执行。
        client.session.trust_env = False
        yield client


def login_client(url, username):
    client = APIClient(url, timeout=3, max_retries=0)
    client.session.trust_env = False
    try:
        response = client.post_json("/login", {"username": username, "password": f"{username}-pass"}, expect_status=200)
        client.set_token(response["token"])
        return client
    except Exception:
        client.close()
        raise


@pytest.fixture
def alice_client(local_api_url):
    with login_client(local_api_url, "alice") as client:
        yield client


@pytest.fixture
def bob_client(local_api_url):
    with login_client(local_api_url, "bob") as client:
        yield client


@pytest.fixture
def task_factory(alice_client, bob_client):
    # 两个客户端都作为依赖，保证清理发生在任一 session 关闭之前。
    created = []

    def create(title=None, client=None):
        owner_client = client if client is not None else alice_client
        task = owner_client.post_json("/tasks", {"title": title if title is not None else f"case-{uuid4().hex}"})
        # 在调用方断言之前登记，后续失败也能进入清理。
        created.append((owner_client, task["id"]))
        return task

    yield create
    errors = []
    for client, task_id in reversed(created):
        try:
            client.delete(f"/tasks/{task_id}", expect_status=(204, 404))
        except Exception as exc:
            errors.append(f"task {task_id}: {exc}")
    if errors:
        pytest.fail("资源清理失败: " + "; ".join(errors))
