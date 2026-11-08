# 阶段九：完成一次需求变更，并交付自己的作品

[每日目录](README.md) · [上一阶段](08-jmeter.md) · [练习 04](../../exercises/exercise_04_framework.md) · [最终交付标准](../DELIVERY.md)

本周才开始实现 archived；前八阶段的靶场只支持 open/done。目标规则以练习 04 为准。已有自己的代码变更时先保存并检查差异，本周只改与归档有关的部分。学习记录与提交说明必须区分教程已有内容与个人新增。

<a id="day-1"></a>

## 第 1 天：把新需求拆成设计、状态表与风险

**材料：** 练习 04 全文、现有 `API_CONTRACT.md`、服务的 `collection/resource`。

**操作：**

1. 新建 `docs/change_archive.md`，写一页设计：目标、允许/拒绝的转换、列表兼容性、鉴权、原子性、数据存储、影响文件、未覆盖范围。
2. 画 open/done/archived 三行三列转换表。明确 open↔done、done→archived 允许；open→archived、archived→其他状态拒绝 409。
3. 列未约定问题：例如 archived→archived 的仅状态请求如何处理。先列“待确认”，主线不擅自增加预期。
4. 列至少 12 条归档用例：成功、拒绝、title 锁定、默认列表排除、include_archived true/false/非法、权限、失败原子性、可查/可删。
5. 分析服务现有表结构：status 是 TEXT、无 CHECK 枚举；添加值通常无需新增列，仍需解释旧数据为何可用。训练库有自己的约束，不能顺手当服务迁移脚本。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

设计是可以交付的一页成品，状态表与15条用例写出完整预期。原需求未明确的自转换/重复参数以“参考选择”单列，不把实现决策冒充已经确认的契约。

文件 `docs/change_archive.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day01/docs/change_archive.md)

```markdown
# 任务归档变更设计（参考成品）

目标：新增archived状态，保留原有open/done与权限语义。

| 当前→目标 | open | done | archived |
|---|---|---|---|
| open | 200不变 | 200 | 409 |
| done | 200 | 200不变 | 200 |
| archived | 409 | 409 | 参考实现按无变化200处理，需需求确认 |

已归档可查、可删，不允许提交title修改（409）；拒绝更新不得部分写入。
GET /tasks默认及include_archived=false不含归档；true包含全部自己的任务；其他值400。
归档仍不可被Bob读、写、删，列表仅返回当前用户，按ID升序。

实现取舍：服务tasks.status为TEXT无CHECK，无需新增列；旧open/done数据继续可用。
训练库的CHECK约束不是服务结构，不能直接拿训练库迁移。
资源更新先校验全部字段和状态转换，再一次UPDATE并提交。
列表保留owner参数绑定，再按归档过滤；解析query时保留空值以拒绝空参数。

参考实现的额外选择：重复include_archived参数返回400；archived→archived且无title为无变化200。
这两项原练习未明确约定，应在真实需求确认后决定，主线验收不把它们当原始事实。
不覆盖：生产登录、异步写入、并发更新锁、生产容量及MySQL迁移。

影响文件：sandbox/task_api.py、Schema、接口契约、用例、落库测试和JMeter计划。
风险：默认列表泄漏归档项、错误转换部分更新、修改title被放行、权限回归、清理漏掉归档项。
```

文件 `docs/archive_cases.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day01/docs/archive_cases.md)

```markdown
# 归档用例（参考设计）

| 编号 | 前置/操作 | 预期 |
|---|---|---|
| A01 | done→archived | 200；GET同ID为archived |
| A02 | open→archived | 409；原值不变 |
| A03 | archived→open | 409；原值不变 |
| A04 | archived→done | 409；原值不变 |
| A05 | archived修改title | 409；完整对象不变 |
| A06 | archived查询 | 200；ID/owner/状态正确 |
| A07 | archived删除后再查 | 204空体→404 |
| A08 | 默认列表 | 含本次open/done，不含archived |
| A09 | include_archived=false | 同默认 |
| A10 | include_archived=true | 本次三状态都存在，仅当前用户 |
| A11 | 参数为other或空字符串 | 400 |
| A12 | Bob读/改/删Alice归档 | 均403；Alice再查未变 |
| A13 | open提交合法新title+archived | 409；title/status均不变 |
| A14 | SQL核对归档成功 | 同ID/owner的status为archived |
| A15 | SQL核对被拒转换 | before/open均不变 |

所有资源由工厂登记，归档可DELETE清理；HTTP与SQL断言分别证明公开行为和落库。
```

**对照运行后的结果：** 设计、状态表、15条用例齐全，能解释兼容性、迁移取舍与主要风险。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 一页设计、转换表、至少 12 条有预期依据的用例，未约定项单列。
- [ ] 列出服务、契约、Schema、测试、JMeter 各需改变什么及兼容性。
- [ ] 能解释为何新增枚举值不等于只有一处字符串修改。

**卡住时：** 先明确业务规则再选实现方式；目前没有答案的自转换，不用“当前返回什么”替代需求确认。

<a id="day-2"></a>

## 第 2 天：先更新契约与用例，写出有意义的失败测试

**操作：**

1. 在 `docs/API_CONTRACT.md` 补归档规则，更新用例设计或链接新设计；标明这是本次变更后的目标行为。
2. 新建 `tests/workflow/test_archive.py`，只用现有 fixture，先写 done→archived 成功并 GET 确认、open→archived 409、已归档 title 修改 409 三条。
3. 归档资源必须先通过 API 创建 open、改为 done、再 archived，不能 SQL 直接塞入跳过状态验证。可把此准备抽成本文件 function fixture，资源仍由工厂登记清理。
4. 补列表三种参数与非法值的参数化测试，并给出当前资源存在/不存在的业务断言。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_archive.py -v --tb=short
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

提供整个归档测试文件，避免只给函数名。make_state仅通过HTTP准备资源，不绕过转换规则。今天旧实现不支持归档，应先跑最前两条看到状态差异；完整文件会到第4天实现列表后才全绿。

文件 `tests/workflow/test_archive.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day02/tests/workflow/test_archive.py)

```python
import pytest
from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def make_state(alice_client, task_factory, state):
    task = task_factory("archive-case")
    path = f"/tasks/{task['id']}"
    if state in ("done", "archived"):
        task = alice_client.put_json(path, {"status": "done"})
    if state == "archived":
        task = alice_client.put_json(path, {"status": "archived"})
    return task


def test_done_to_archived_transition(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "done")
    path = f"/tasks/{task['id']}"
    archived = alice_client.put_json(path, {"status": "archived"})
    assert archived == {**task, "status": "archived"}
    assert alice_client.get_json(path) == archived


def test_open_to_archived_transition_is_conflict(alice_client, task_factory):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "archived"}, expect_status=409)
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("before,after,expected", [
    ("open", "open", 200), ("open", "done", 200), ("done", "open", 200),
    ("done", "done", 200), ("done", "archived", 200), ("open", "archived", 409),
    ("archived", "open", 409), ("archived", "done", 409),
], ids=["open-open", "open-done", "done-open", "done-done", "done-archive", "open-archive", "archive-open", "archive-done"])
def test_transition_matrix(alice_client, task_factory, before, after, expected):
    task = make_state(alice_client, task_factory, before)
    path = f"/tasks/{task['id']}"
    result = alice_client.put_json(path, {"status": after}, expect_status=expected)
    if expected == 200:
        assert result == {**task, "status": after}
        assert_schema(result, TASK_SCHEMA)
        assert alice_client.get_json(path) == result
    else:
        assert alice_client.get_json(path) == task


def test_archived_title_is_locked(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "changed"}, expect_status=409)
    assert alice_client.get_json(path) == task


def test_archived_can_be_deleted(alice_client, task_factory):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    assert alice_client.delete(path, expect_status=204).content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}


@pytest.mark.parametrize("query", ["", "?include_archived=false"], ids=["default", "false"])
def test_default_list_excludes_archived(alice_client, task_factory, query):
    active = make_state(alice_client, task_factory, "open")
    done = make_state(alice_client, task_factory, "done")
    archived = make_state(alice_client, task_factory, "archived")
    items = alice_client.get_json("/tasks" + query)["items"]
    ids = [item["id"] for item in items]
    assert active["id"] in ids and done["id"] in ids
    assert archived["id"] not in ids
    assert all(item["status"] != "archived" for item in items)
    assert ids == sorted(ids)


def test_include_archived_lists_only_own_tasks(alice_client, bob_client, task_factory):
    own = [make_state(alice_client, task_factory, state) for state in ("open", "done", "archived")]
    other = task_factory("bob-private", client=bob_client)
    items = alice_client.get_json("/tasks?include_archived=true")["items"]
    assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
    ids = [item["id"] for item in items]
    assert all(task["id"] in ids for task in own)
    assert other["id"] not in ids
    assert all(item["owner"] == "alice" for item in items)
    assert ids == sorted(ids)


@pytest.mark.parametrize("value", ["other", "", "TRUE", "1"], ids=["word", "empty", "case", "number"])
def test_invalid_archive_query(alice_client, value):
    result = alice_client.get_json("/tasks", params={"include_archived": value}, expect_status=400)
    assert result == {"error": "invalid_fields"}


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_archived_other_user_forbidden(alice_client, bob_client, task_factory, method):
    task = make_state(alice_client, task_factory, "archived")
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task
```

文件 `docs/API_CONTRACT.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day02/docs/API_CONTRACT.md)

变更后的完整契约；表格中的列表响应还受下方归档规则约束。

```markdown
# 本地任务 API 契约

实现：`sandbox/task_api.py`。以需求为断言依据；发现实现与下列规则不一致时，应报告缺陷，不能直接改预期让测试通过。

## 运行与数据

手动启动：`python -m sandbox.task_api --port 8765 --db reports/tasks.sqlite3`（请使用虚拟环境解释器）。服务只监听 `127.0.0.1`。SQLite 文件保存任务，重启后任务仍在；登录 token 只保存在进程内，重启后需要重新登录。自动测试使用动态端口和临时数据库，无需手动启动。

演示账号：`alice / alice-pass`、`bob / bob-pass`。这是公开的本地教学数据；真实环境凭据通过环境变量或 CI secrets 注入，不提交到仓库。登录仅演示 token 流转，不包含密码哈希、过期、撤销或生产登录防护。

## 端点

除 health/login 外都需要 `Authorization: Bearer <token>`。错误统一返回 `{"error": "错误代码"}`；每次响应带 `X-Request-ID`，便于关联问题。没有 token、无效 token 均为 401；已登录但访问他人任务为 403。合法整数 ID 不存在为 404；格式无效的任务 ID 也为 404。错误参数不得改变数据。

| 方法与路径 | 输入 | 成功结果 | 主要失败 |
|---|---|---|---|
| GET `/health` | 无 | 200，`{"status":"ok"}` | — |
| POST `/login` | username、password 字符串 | 200，token、username | 错误凭据 401；非法 JSON / 非对象 400 |
| POST `/tasks` | title | 201，完整任务，Location 指向新任务 | title 非法或含未知字段 400 |
| GET `/tasks` | include_archived=true/false（可选） | 200，`{"items":[...]}`，仅当前用户，按 id 升序；默认排除归档 | 参数非法 400 |
| GET `/tasks/{id}` | 无 | 200，完整任务 | 403 / 404 |
| PUT `/tasks/{id}` | title 或 status，至少一个 | 200，更新后的完整任务 | 空对象、未知字段或字段非法 400；归档状态冲突或title锁定 409 |
| DELETE `/tasks/{id}` | 无 | 204，响应体为空 | 删除后再次访问 404 |

PUT 在本练习中约定为部分字段更新；实际项目必须遵循目标接口的约定，不从 HTTP 方法名推断全部业务规则。

任务结构：`id` 为正整数；`title` 为字符串；`status` 可为 `open`、`done` 或 `archived`；`owner` 是创建用户。创建时状态总是 `open`，客户端不能指定 owner、id 或 status。title 去除首尾空白后长度必须为 1—80（Python Unicode 字符数），空字符串、全空白、非字符串都为 400。PUT 允许在 open/done 间切换、done→archived；open→archived 和 archived→其他状态为409；归档后不可修改title。批量更新要么全部合法并写入，要么全部不写入。

未匹配路径返回 404；本靶场实现的四种方法访问已知路径但不受支持时返回 405。未实现方法、分页、并发更新控制、幂等键和限流不属于当前契约；自行增加前先补需求与测试。

## 闭环与权限的预期

创建返回 ID → 按这个 ID 查询得到相同字段 → 更新 → 再查确认持久化 → 删除 → 再查 404。另一个用户应无法读取、更新或删除此资源，且列表不能泄露它。Schema 只检查结构，必须另外断言 owner、字段值与数据变化。


# 归档变更契约补充

任务status增加archived；创建仍仅open，客户端不能指定初始status。
open/done可互转，done可归档；open归档及archived转其他状态返回409。
已归档可查询、可删除，title修改返回409。非法更新不得部分写入。
列表默认和include_archived=false排除archived；true返回全部自己的任务；其他值400。
身份、越权、字段保护、排序和原有长度规则不变。
附加参考选择及待确认项见change_archive.md。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
# 故意失败实验，预期退出码 1；核对下面的结果说明。
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_archive.py::test_done_to_archived_transition tests/workflow/test_archive.py::test_open_to_archived_transition_is_conflict -q
```

**对照运行后的结果：** 旧实现下最前两条在HTTP期望处失败；不能因抛错就改预期成400。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 至少一条在旧实现的状态码/业务值上失败，原因是尚未支持归档，非导入/语法错误。
- [ ] 保存变更前失败证据，预期均来自练习 04；不会把 409 改成当前的 400 让它绿。
- [ ] 旧功能基线仍可独立运行，已记录哪些失败是本次预期新增行为。

**卡住时：** 已归档 fixture 准备失败会显示 ERROR；先用 done→archived 直接测试证明缺口，再逐步实现。

<a id="day-3"></a>

## 第 3 天：实现状态转换、title 锁定与失败原子性

**材料：** `sandbox/task_api.py::TaskHandler.resource`、新状态表。

**操作：**

1. 在 `resource` 分开字段合法性校验与状态冲突校验；成功前先算出目标 title/status，全部检查通过才写数据库。
2. 支持 done→archived；拒绝 open→archived、archived→open/done；已 archived 修改 title 返回 409。
3. 扩充测试：每种允许/拒绝转换用可读 ids；拒绝时再 GET 完整原对象，包含 title 与 status 不变。
4. 更新 `TASK_SCHEMA` 中状态枚举，并检查自己新增文件是否也复制了枚举定义；更新允许值时保留未知值的拒绝测试。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_archive.py -k 'transition or title' -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks.py -v
```

测试名包含 transition/title 以便命令选中；列表相关尚未实现时可保留相应已知失败到第 4 天。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

完整服务代码保留现有鉴权和数据库处理，仅resource增加状态校验。非法字段仍400、状态冲突409；校验结束才写库。Schema加archived允许值不会删除旧场景。

文件 `sandbox/task_api.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day03/sandbox/task_api.py)

这是仅完成状态转换后的服务完整文件；与自己的实现对比，先保留个人改动再合并。列表过滤在明天完成。

```python
"""任务业务靶场：标准库 HTTP + SQLite。契约见 docs/API_CONTRACT.md。"""
from __future__ import annotations

import argparse
import json
import sqlite3
import threading
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

# 公开演示数据，不能作为实际环境的认证实现。
DEMO_USERS = {"alice": "alice-pass", "bob": "bob-pass"}


class TaskServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tokens: dict[str, str] = {}
        self.token_lock = threading.Lock()
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, status TEXT NOT NULL, owner TEXT NOT NULL
            )""")
            db.commit()
        super().__init__(address, TaskHandler)


class TaskHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 不使用默认访问日志，避免记录 URL/query 等原始输入。
        pass

    def reply(self, status, body=None, headers=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Request-ID", uuid4().hex)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def error(self, status, code):
        self.reply(status, {"error": code})

    def read_object(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise ValueError("invalid length")
            value = json.loads(self.rfile.read(size))
            if not isinstance(value, dict):
                raise ValueError("expected object")
            return value
        except (ValueError, UnicodeDecodeError):
            self.error(400, "invalid_json_object")
            return None

    def dispatch(self):
        path = urlsplit(self.path).path
        if path == "/health":
            if self.command != "GET":
                return self.error(405, "method_not_allowed")
            return self.reply(200, {"status": "ok"})
        if path == "/login":
            if self.command != "POST":
                return self.error(405, "method_not_allowed")
            body = self.read_object()
            if body is None:
                return
            username, password = body.get("username"), body.get("password")
            if (not isinstance(username, str) or not isinstance(password, str)
                    or DEMO_USERS.get(username) != password):
                return self.error(401, "invalid_credentials")
            token = uuid4().hex
            with self.server.token_lock:
                self.server.tokens[token] = username
            return self.reply(200, {"token": token, "username": username})

        parts = path.strip("/").split("/")
        if path != "/tasks" and not (len(parts) == 2 and parts[0] == "tasks"):
            return self.error(404, "not_found")
        auth = self.headers.get("Authorization", "")
        with self.server.token_lock:
            username = self.server.tokens.get(auth.removeprefix("Bearer ")) if auth.startswith("Bearer ") else None
        if username is None:
            return self.error(401, "unauthorized")
        # 显式提交写操作；closing 负责关闭连接，sqlite 的 with 本身不负责 close。
        with closing(sqlite3.connect(self.server.db_path, timeout=5)) as db:
            db.row_factory = sqlite3.Row
            if path == "/tasks":
                return self.collection(db, username)
            try:
                task_id = int(parts[1])
                if not 0 < task_id <= 2**63 - 1:
                    raise ValueError("invalid id")
            except ValueError:
                return self.error(404, "not_found")
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                return self.error(404, "not_found")
            if row["owner"] != username:
                return self.error(403, "forbidden")
            return self.resource(db, row)

    def collection(self, db, username):
        if self.command == "GET":
            rows = db.execute("SELECT * FROM tasks WHERE owner=? ORDER BY id", (username,)).fetchall()
            return self.reply(200, {"items": [dict(row) for row in rows]})
        if self.command != "POST":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if set(body) != {"title"} or not self.valid_title(body.get("title")):
            return self.error(400, "invalid_fields")
        title = body["title"].strip()
        cursor = db.execute("INSERT INTO tasks(title,status,owner) VALUES (?, 'open', ?)", (title, username))
        task_id = cursor.lastrowid
        db.commit()
        self.reply(201, {"id": task_id, "title": title, "status": "open", "owner": username},
                   {"Location": f"/tasks/{task_id}"})

    @staticmethod
    def valid_title(title):
        return isinstance(title, str) and 1 <= len(title.strip()) <= 80

    def resource(self, db, row):
        if self.command == "GET":
            return self.reply(200, dict(row))
        if self.command == "DELETE":
            db.execute("DELETE FROM tasks WHERE id=?", (row["id"],))
            db.commit()
            return self.reply(204)
        if self.command != "PUT":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if (not body or set(body) - {"title", "status"}
                or ("title" in body and not self.valid_title(body["title"]))
                or ("status" in body and body["status"] not in ("open", "done", "archived"))):
            return self.error(400, "invalid_fields")
        status = body.get("status", row["status"])
        # 先验证所有业务冲突，再执行一次UPDATE，避免部分写入。
        if row["status"] == "archived":
            if "title" in body or status != "archived":
                return self.error(409, "state_conflict")
        elif row["status"] == "open" and status == "archived":
            return self.error(409, "state_conflict")
        title = body["title"].strip() if "title" in body else row["title"]
        db.execute("UPDATE tasks SET title=?,status=? WHERE id=?", (title, status, row["id"]))
        db.commit()
        self.reply(200, {**dict(row), "title": title, "status": status})

    do_GET = dispatch
    do_POST = dispatch
    do_PUT = dispatch
    do_DELETE = dispatch


def create_server(db_path: Path, port: int = 0) -> TaskServer:
    return TaskServer(("127.0.0.1", port), db_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=Path("reports/tasks.sqlite3"))
    args = parser.parse_args()
    server = create_server(args.db, args.port)
    print(f"Local task API: http://127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```

文件 `tests/workflow/test_tasks.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day03/tests/workflow/test_tasks.py)

完整旧功能测试，仅Schema增加合法归档值；原有业务断言保持。

```python
"""需求驱动的本地 HTTP 集成测试；不读取服务端数据库来代替业务断言。"""
import pytest

from core.validator import assert_schema

pytestmark = pytest.mark.integration

TASK_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "status", "owner"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1, "maxLength": 80},
        "status": {"enum": ["open", "done", "archived"]},
        "owner": {"type": "string"},
    },
}


@pytest.mark.smoke
def test_full_crud(alice_client, task_factory):
    """TASK-01：同一个 ID 的持久化闭环，而不是几个无关请求。"""
    created = task_factory("first")
    assert_schema(created, TASK_SCHEMA)
    assert created["owner"] == "alice"
    assert created["status"] == "open"
    path = f"/tasks/{created['id']}"
    assert alice_client.get_json(path) == created
    updated = alice_client.put_json(path, {"title": "changed", "status": "done"})
    assert updated == {**created, "title": "changed", "status": "done"}
    assert alice_client.get_json(path) == updated
    deleted = alice_client.delete(path, expect_status=204)
    assert deleted.content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
    alice_client.delete(path, expect_status=404)


@pytest.mark.parametrize("token", [None, "not-a-valid-token"], ids=["missing", "invalid"])
def test_authentication_required(anonymous_client, token, alice_client):
    """TASK-02/03：拒绝写入，也不产生新任务。"""
    before = alice_client.get_json("/tasks")
    if token:
        anonymous_client.set_token(token)
    result = anonymous_client.post_json("/tasks", {"title": "must-not-exist"}, expect_status=401)
    assert result == {"error": "unauthorized"}
    assert alice_client.get_json("/tasks") == before


def test_invalid_login(anonymous_client):
    result = anonymous_client.post_json("/login", {"username": "alice", "password": "wrong"}, expect_status=401)
    assert result == {"error": "invalid_credentials"}


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_other_user_cannot_access_task(method, alice_client, bob_client, task_factory):
    """TASK-04：携带另一个合法用户的 token，也必须拒绝越权。"""
    task = task_factory()
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task


def test_list_is_scoped_to_current_user(alice_client, bob_client, task_factory):
    alice_task = task_factory()
    bob_task = task_factory(client=bob_client)
    for client, username, own, other in [
        (alice_client, "alice", alice_task, bob_task),
        (bob_client, "bob", bob_task, alice_task),
    ]:
        items = client.get_json("/tasks")["items"]
        assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
        assert own in items
        assert other["id"] not in [item["id"] for item in items]
        assert all(item["owner"] == username for item in items)


@pytest.mark.parametrize("title", ["", "   ", None, 123, [], "x" * 81],
                         ids=["empty", "blank", "null", "number", "array", "too-long"])
def test_invalid_title_does_not_create_task(alice_client, title):
    before = alice_client.get_json("/tasks")
    response = alice_client.post_json("/tasks", {"title": title}, expect_status=400)
    assert response == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("title", ["x", "x" * 80, "  normalized  "], ids=["min", "max", "trim"])
def test_title_boundaries_and_normalization(alice_client, task_factory, title):
    task = task_factory(title)
    assert task["title"] == title.strip()
    assert_schema(task, TASK_SCHEMA)
    assert alice_client.get_json(f"/tasks/{task['id']}") == task


@pytest.mark.parametrize("body", [
    {}, {"title": "valid", "owner": "bob"}, {"title": "valid", "id": 9},
    {"title": "valid", "status": "done"},
], ids=["missing-title", "owner-protected", "id-protected", "status-protected"])
def test_create_rejects_unknown_or_missing_fields(alice_client, body):
    before = alice_client.get_json("/tasks")
    alice_client.post_json("/tasks", body, expect_status=400)
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("body", [
    {"title": "changed", "status": "unknown"}, {"title": "changed", "status": None},
    {}, {"owner": "bob"}, {"id": 2}, {"title": " "},
], ids=["bad-status", "null-status", "empty", "owner", "id", "blank-title"])
def test_invalid_update_is_atomic(alice_client, task_factory, body):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, body, expect_status=400)
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_missing_resource(alice_client, task_factory, method):
    task = task_factory()
    path = f"/tasks/{task['id']}"
    alice_client.delete(path, expect_status=204)
    kwargs = {"json": {"title": "changed"}} if method == "PUT" else {}
    assert alice_client.request(method, path, expect_status=404, **kwargs).json() == {"error": "not_found"}


def test_invalid_json_keeps_service_available(alice_client):
    before = alice_client.get_json("/tasks")
    response = alice_client.request("POST", "/tasks", expect_status=400,
                                    data='{', headers={"Content-Type": "application/json"})
    assert response.json() == {"error": "invalid_json_object"}
    assert response.headers["X-Request-ID"]
    assert alice_client.get_json("/health") == {"status": "ok"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("task_id", ["invalid", "0", "-1", "9" * 30],
                         ids=["text", "zero", "negative", "overflow"])
def test_invalid_resource_id_returns_404(alice_client, task_id):
    """非法或超出数据库整数范围的 ID，不应导致连接中断或 500。"""
    result = alice_client.get_json(f"/tasks/{task_id}", expect_status=404)
    assert result == {"error": "not_found"}
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_archive.py -k 'transition or title or delete' -q
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks.py -q
```

**对照运行后的结果：** 12条转换/title/删除相关场景通过，旧功能测试通过；列表场景留到明天完成。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 允许转换落库并可再查，拒绝转换返回 409 且完整原值不变。
- [ ] 已归档可查询、可删除，title 锁定测试通过。
- [ ] 原有 open/done 测试仍通过；没有先更新 title 再验证 status 的部分写入。

**卡住时：** 修改枚举后别让所有不认识的 status 都变 409；非法参数与合法值之间的业务冲突要按契约区分。

<a id="day-4"></a>

## 第 4 天：实现列表过滤并保住权限隔离

**材料：** `TaskHandler.dispatch/collection`、Python `urlsplit/parse_qs`。

**操作：**

1. 在 dispatch 保留 path 路由的同时解析 query，将 include_archived 校验传给列表逻辑；仅 `true/false` 合法，其他值 400。对空值显式保留并校验，避免解析器丢弃后当成默认。
2. 默认和 false 过滤 archived；true 包含自己的所有任务；保持按 id 升序。重复参数行为未约定时列问题，不擅自宣称已覆盖。
3. Alice 准备 open/done/archived，Bob 另建任务；断言三种列表语义、全部元素 owner、Bob 不可读/改/删 Alice 的 archived 任务。
4. 更新设计表，复核非法参数、未知字段及旧权限逻辑。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_archive.py -v
.\.venv\Scripts\python.exe -m pytest tests/workflow -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

dispatch用path路由，但self.path仍保留原URL，因此可以在collection直接解析query，不必重新传参。keep_blank_values=True确保空字符串被判400；owner仍使用绑定参数。

文件 `sandbox/task_api.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day04/sandbox/task_api.py)

完整最终归档服务：在昨天版本上补query解析、合法值校验、默认过滤和owner隔离。

```python
"""任务业务靶场：标准库 HTTP + SQLite。契约见 docs/API_CONTRACT.md。"""
from __future__ import annotations

import argparse
import json
import sqlite3
import threading
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from uuid import uuid4

# 公开演示数据，不能作为实际环境的认证实现。
DEMO_USERS = {"alice": "alice-pass", "bob": "bob-pass"}


class TaskServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tokens: dict[str, str] = {}
        self.token_lock = threading.Lock()
        with closing(sqlite3.connect(self.db_path)) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, status TEXT NOT NULL, owner TEXT NOT NULL
            )""")
            db.commit()
        super().__init__(address, TaskHandler)


class TaskHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # 不使用默认访问日志，避免记录 URL/query 等原始输入。
        pass

    def reply(self, status, body=None, headers=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Request-ID", uuid4().hex)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def error(self, status, code):
        self.reply(status, {"error": code})

    def read_object(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise ValueError("invalid length")
            value = json.loads(self.rfile.read(size))
            if not isinstance(value, dict):
                raise ValueError("expected object")
            return value
        except (ValueError, UnicodeDecodeError):
            self.error(400, "invalid_json_object")
            return None

    def dispatch(self):
        path = urlsplit(self.path).path
        if path == "/health":
            if self.command != "GET":
                return self.error(405, "method_not_allowed")
            return self.reply(200, {"status": "ok"})
        if path == "/login":
            if self.command != "POST":
                return self.error(405, "method_not_allowed")
            body = self.read_object()
            if body is None:
                return
            username, password = body.get("username"), body.get("password")
            if (not isinstance(username, str) or not isinstance(password, str)
                    or DEMO_USERS.get(username) != password):
                return self.error(401, "invalid_credentials")
            token = uuid4().hex
            with self.server.token_lock:
                self.server.tokens[token] = username
            return self.reply(200, {"token": token, "username": username})

        parts = path.strip("/").split("/")
        if path != "/tasks" and not (len(parts) == 2 and parts[0] == "tasks"):
            return self.error(404, "not_found")
        auth = self.headers.get("Authorization", "")
        with self.server.token_lock:
            username = self.server.tokens.get(auth.removeprefix("Bearer ")) if auth.startswith("Bearer ") else None
        if username is None:
            return self.error(401, "unauthorized")
        # 显式提交写操作；closing 负责关闭连接，sqlite 的 with 本身不负责 close。
        with closing(sqlite3.connect(self.server.db_path, timeout=5)) as db:
            db.row_factory = sqlite3.Row
            if path == "/tasks":
                return self.collection(db, username)
            try:
                task_id = int(parts[1])
                if not 0 < task_id <= 2**63 - 1:
                    raise ValueError("invalid id")
            except ValueError:
                return self.error(404, "not_found")
            row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None:
                return self.error(404, "not_found")
            if row["owner"] != username:
                return self.error(403, "forbidden")
            return self.resource(db, row)

    def collection(self, db, username):
        if self.command == "GET":
            parameters = parse_qs(urlsplit(self.path).query, keep_blank_values=True)
            values = parameters.get("include_archived")
            if values is None:
                include_archived = False
            elif len(values) == 1 and values[0] in ("true", "false"):
                include_archived = values[0] == "true"
            else:
                return self.error(400, "invalid_fields")
            query = "SELECT * FROM tasks WHERE owner=?"
            if not include_archived:
                query += " AND status != 'archived'"
            query += " ORDER BY id"
            rows = db.execute(query, (username,)).fetchall()
            return self.reply(200, {"items": [dict(row) for row in rows]})
        if self.command != "POST":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if set(body) != {"title"} or not self.valid_title(body.get("title")):
            return self.error(400, "invalid_fields")
        title = body["title"].strip()
        cursor = db.execute("INSERT INTO tasks(title,status,owner) VALUES (?, 'open', ?)", (title, username))
        task_id = cursor.lastrowid
        db.commit()
        self.reply(201, {"id": task_id, "title": title, "status": "open", "owner": username},
                   {"Location": f"/tasks/{task_id}"})

    @staticmethod
    def valid_title(title):
        return isinstance(title, str) and 1 <= len(title.strip()) <= 80

    def resource(self, db, row):
        if self.command == "GET":
            return self.reply(200, dict(row))
        if self.command == "DELETE":
            db.execute("DELETE FROM tasks WHERE id=?", (row["id"],))
            db.commit()
            return self.reply(204)
        if self.command != "PUT":
            return self.error(405, "method_not_allowed")
        body = self.read_object()
        if body is None:
            return
        if (not body or set(body) - {"title", "status"}
                or ("title" in body and not self.valid_title(body["title"]))
                or ("status" in body and body["status"] not in ("open", "done", "archived"))):
            return self.error(400, "invalid_fields")
        status = body.get("status", row["status"])
        # 先验证所有业务冲突，再执行一次UPDATE，避免部分写入。
        if row["status"] == "archived":
            if "title" in body or status != "archived":
                return self.error(409, "state_conflict")
        elif row["status"] == "open" and status == "archived":
            return self.error(409, "state_conflict")
        title = body["title"].strip() if "title" in body else row["title"]
        db.execute("UPDATE tasks SET title=?,status=? WHERE id=?", (title, status, row["id"]))
        db.commit()
        self.reply(200, {**dict(row), "title": title, "status": status})

    do_GET = dispatch
    do_POST = dispatch
    do_PUT = dispatch
    do_DELETE = dispatch


def create_server(db_path: Path, port: int = 0) -> TaskServer:
    return TaskServer(("127.0.0.1", port), db_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=Path("reports/tasks.sqlite3"))
    args = parser.parse_args()
    server = create_server(args.db, args.port)
    print(f"Local task API: http://127.0.0.1:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_archive.py tests/workflow/test_tasks.py -q
```

**对照运行后的结果：** 22条归档场景及原有业务场景通过，实际数量以collection为准。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 新用例全部通过；true/false/缺失/非法值有业务断言，权限未泄漏。
- [ ] 核对三种状态时使用本测试生成的 ID，不依赖全库恰好三条。
- [ ] 能解释 URL query 与 JSON body 的解析位置不同。

**卡住时：** 只对 `urlsplit(self.path).path` 路由会忽略 query；不要用整段 URL 直接比较 `/tasks`。

<a id="day-5"></a>

## 第 5 天：补 SQL、清理与 Linux/CI 回归

**操作：**

1. 用 `local_api_db` 加归档后的只读 SQL 断言，确认 status=archived；对非法 open→archived 加 title/status 都不变的落库断言。
2. 确认 archived 仍可删除，工厂在测试提前失败时也能回收；重用第三阶段的清理验证方法，不靠“默认列表为空”判断 archived 已删。
3. Windows 跑本地并行和报告；Linux 在包含本次改动的工作副本跑脚本。两边先核对代码提交/差异一致。

```powershell
.\.venv\Scripts\python.exe -m pytest -n 2 --html=reports/learning/archive/report.html --self-contained-html --junitxml=reports/learning/archive/junit.xml
```

```bash
PYTHON_BIN="$PWD/.venv-linux/bin/python" REPORT_DIR="$PWD/reports/learning/archive-linux" bash scripts/run_regression.sh
printf 'exit=%s\n' "$?"
```

4. 本地验收通过后推送到自己的练习分支，等待两个 OS 的 CI，下载报告与版本记录。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

追加两条SQL测试；不要用SQL准备archived绕过HTTP转换。默认列表看不到archived不代表它已删，应按ID查询或用包含归档的列表核对清理。并行脚本只证明本地部分，Linux/CI需另行执行。

文件 `tests/workflow/test_archive.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/09/day05/tests/workflow/test_archive.py)

```python
def read_archive_row(db_path, task_id):
    from contextlib import closing
    import sqlite3
    with closing(sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        return db.execute("SELECT title,status,owner FROM tasks WHERE id=? AND owner=?",
                          (task_id, "alice")).fetchone()


def test_archive_is_persisted(alice_client, task_factory, local_api_db):
    task = make_state(alice_client, task_factory, "archived")
    assert read_archive_row(local_api_db, task["id"]) == (task["title"], "archived", "alice")


def test_archive_conflict_is_atomic_in_database(alice_client, task_factory, local_api_db):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    alice_client.put_json(path, {"title": "after", "status": "archived"}, expect_status=409)
    assert alice_client.get_json(path) == task
    assert read_archive_row(local_api_db, task["id"]) == ("before", "open", "alice")
```

文件 `exercises/archive_regression.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day05/exercises/archive_regression.ps1)

```powershell
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force reports/learning/archive | Out-Null
.\.venv\Scripts\python.exe -m pytest -n 2 --html=reports/learning/archive/report.html --self-contained-html --junitxml=reports/learning/archive/junit.xml
if ($LASTEXITCODE -ne 0) { throw '归档完整并行回归失败' }
Write-Output '本地通过；还需在相同代码版本的Linux和自己的远程CI验证。'
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow -n 2 -q
& .\exercises\archive_regression.ps1
```

**对照运行后的结果：** 归档与旧workflow并行通过，成功/冲突两种落库结果符合预期。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] SQL 成功/拒绝断言通过，资源清理覆盖 archived。
- [ ] Windows、真实 Linux、并行及 CI 均通过，证据指向本次代码版本。
- [ ] 旧测试无不必要删除、skip 或修改预期来掩盖回归。

**卡住时：** 更新了 Windows 工作区但 Linux 副本仍旧时先同步个人改动，不能把旧版通过当新版验收。

<a id="day-6"></a>

## 第 6 天：为归档补 JMeter 断言，完成一次缺陷检出

**材料：** 自己的正确 JMX、排障模板、归档测试。

**操作：**

1. 从正确计划另存 `performance/my_archive_workflow.jmx`。在 `05_verify_update` 后、删除前添加两个 sampler：PUT 同 ID status=archived（200）；GET `/tasks?include_archived=true`（200），业务断言返回列表包含当前 task_id 且 status=archived、owner=alice。
2. 原有每轮六请求增加为八请求，登录仍每线程一次。1 线程×3 轮现在应有 `1+8×3=25` 样本。沿用阶段八命令，改计划名、新结果目录、新 run_id，用检查器 `--expected-samples 25`。
3. 确保手动服务已重启加载本次归档实现；pytest 会新启服务，但手动 JMeter 服务不会自动热更新。
4. 临时去掉默认列表排除 archived 的一处过滤，跑归档列表测试，确认在业务断言失败；恢复后重跑。在 `docs/bug_report_archive.md` 写缺陷报告，标明是主动注入。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

完整JMX增加归档PUT和列表GET两步，新增业务断言匹配当前ID/owner/status。common清理使用包含归档的列表。故障脚本验证默认过滤的业务断言，finally恢复源码；手动JMeter服务要先重启加载新代码。

文件 `performance/my_archive_workflow.jmx` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day06/performance/my_archive_workflow.jmx)

```xml
<?xml version='1.0' encoding='utf-8'?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Local task API workflow" enabled="true">
      <stringProp name="TestPlan.comments">Archive workflow: 1 login per thread, 8 business requests per loop; default 25 samples.</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments" />
      </elementProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Task users" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">stopthread</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">${__P(loops,3)}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">${__P(threads,1)}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">${__P(ramp_up,1)}</stringProp>
        <stringProp name="ThreadGroup.duration" />
        <stringProp name="ThreadGroup.delay" />
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP defaults" enabled="true">
          <stringProp name="HTTPSampler.domain">${__P(host,127.0.0.1)}</stringProp>
          <stringProp name="HTTPSampler.port">${__P(port,8765)}</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
          <stringProp name="HTTPSampler.connect_timeout">3000</stringProp>
          <stringProp name="HTTPSampler.response_timeout">5000</stringProp>
          <stringProp name="HTTPSampler.implementation">HttpClient4</stringProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments" />
          </elementProp>
        </ConfigTestElement>
        <hashTree />
        <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="JSON headers" enabled="true">
          <collectionProp name="HeaderManager.headers">
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Content-Type</stringProp>
              <stringProp name="Header.value">application/json</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree />
        <OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" testname="Login once per thread" enabled="true" />
        <hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="01_login" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"username":"alice","password":"alice-pass"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/login</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract thread token" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">auth_token</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.token</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
        </hashTree>
        <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Task business workflow" enabled="true" />
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="Bearer token" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">Bearer ${auth_token}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree />
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Think time before each business request" enabled="true">
            <stringProp name="ConstantTimer.delay">${__P(think_ms,200)}</stringProp>
          </ConstantTimer>
          <hashTree />
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="02_create" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"title":"jm-${__P(run_id,local)}-${__threadNum}-${__counter(FALSE,)}"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 201" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">201</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract task ID" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">task_id</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.id</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="03_read" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="04_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"status":"done"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">PUT</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="05_verify_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSR223Assertion guiclass="TestBeanGUI" testclass="JSR223Assertion" testname="Persisted task must be done" enabled="true">
              <stringProp name="scriptLanguage">groovy</stringProp>
              <stringProp name="parameters" />
              <stringProp name="filename" />
              <stringProp name="cacheKey">true</stringProp>
              <stringProp name="script">def task = new groovy.json.JsonSlurper().parseText(prev.getResponseDataAsString())
if (task.status != 'done' || task.id.toString() != vars.get('task_id')) {
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage('Expected current task ID and persisted status=done')
}
</stringProp>
            </JSR223Assertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="05a_archive" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"status":"archived"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">PUT</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="05b_list_archived" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks?include_archived=true</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSR223Assertion guiclass="TestBeanGUI" testclass="JSR223Assertion" testname="Current archived task must be listed" enabled="true">
              <stringProp name="scriptLanguage">groovy</stringProp>
              <stringProp name="parameters" />
              <stringProp name="filename" />
              <stringProp name="cacheKey">true</stringProp>
              <stringProp name="script">def data = new groovy.json.JsonSlurper().parseText(prev.getResponseDataAsString())
def task = data.items.find { it.id.toString() == vars.get('task_id') }
if (task == null || task.status != 'archived' || task.owner != 'alice') {
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage('Expected current archived task owned by alice in list')
}</stringProp>
            </JSR223Assertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="06_delete" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">DELETE</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 204" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">204</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="07_verify_deleted" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 404" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">404</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

文件 `exercises/jmeter/common.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day06/exercises/jmeter/common.ps1)

在第八阶段helper上将清理时的列表改为include_archived=true，避免漏掉归档残留。

```powershell
$ErrorActionPreference = 'Stop'
$lessonRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$lessonPython = Join-Path $lessonRoot '.venv/Scripts/python.exe'

function Invoke-LessonJmeter {
    param(
        [Parameter(Mandatory=$true)][string]$Jmeter,
        [Parameter(Mandatory=$true)][string]$Plan,
        [Parameter(Mandatory=$true)][string]$RunName,
        [int]$Threads = 1, [int]$Loops = 3,
        [int]$BusinessRequests = 6, [switch]$ExpectFailure
    )
    if (-not (Test-Path -LiteralPath $Jmeter)) { throw 'JMeter路径不存在' }
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id限30位英数字或连字符' }
    if ($Threads -lt 1 -or $Loops -lt 1) { throw '线程数/循环数必须为正数' }
    $lessonDir = Join-Path $lessonRoot "reports/learning/jmeter/$RunName"
    if (Test-Path -LiteralPath $lessonDir) { throw '结果目录已存在，请换新RunName' }
    New-Item -ItemType Directory -Path $lessonDir | Out-Null
    $lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
    if ($lessonHealth.StatusCode -ne 200) { throw '靶场未就绪' }
    & $Jmeter -n -t $Plan -q performance/jmeter.properties "-Jthreads=$Threads" "-Jloops=$Loops" "-Jramp_up=$Threads" -Jthink_ms=200 "-Jrun_id=$RunName" -l "$lessonDir/results.jtl" -j "$lessonDir/jmeter.log" -e -o "$lessonDir/html"
    $lessonJmeterExit = $LASTEXITCODE
    if ($lessonJmeterExit -ne 0) { throw "JMeter进程失败：$lessonJmeterExit" }
    $lessonExpected = $Threads * (1 + $BusinessRequests * $Loops)
    & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl" --expected-samples $lessonExpected
    $lessonCheckExit = $LASTEXITCODE
    $lessonSamples = @(Import-Csv -LiteralPath "$lessonDir/results.jtl")
    $lessonFailures = @($lessonSamples | Where-Object { $_.success -eq 'false' }).Count
    if ($ExpectFailure) {
        if ($lessonCheckExit -eq 0 -or $lessonFailures -eq 0) { throw '没有验证到预期断言失败' }
        & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl"
        if ($LASTEXITCODE -eq 0) { throw '包含失败样本却未返回非零' }
        Write-Output "预期故障成立：samples=$($lessonSamples.Count) failures=$lessonFailures"
    } else {
        if ($lessonCheckExit -ne 0) { throw 'JTL数量/断言检查失败' }
        Write-Output "通过：samples=$($lessonSamples.Count) failures=$lessonFailures expected=$lessonExpected"
    }
}

function Remove-LessonTasks {
    param([Parameter(Mandatory=$true)][string]$RunName)
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id非法' }
    $lessonLogin = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/login -ContentType 'application/json' -Body '{"username":"alice","password":"alice-pass"}'
    $lessonHeaders = @{ Authorization = "Bearer $($lessonLogin.token)" }
    $lessonItems = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks?include_archived=true -Headers $lessonHeaders).items
    $lessonPrefix = "jm-$RunName-"
    $lessonTargets = @($lessonItems | Where-Object { $_.title.StartsWith($lessonPrefix) })
    foreach ($lessonTask in $lessonTargets) {
        Write-Output "清理本轮任务：id=$($lessonTask.id) title=$($lessonTask.title)"
        $lessonDelete = Invoke-WebRequest -UseBasicParsing -Method Delete -Uri "http://127.0.0.1:8765/tasks/$($lessonTask.id)" -Headers $lessonHeaders
        if ($lessonDelete.StatusCode -ne 204) { throw '资源清理失败' }
    }
    $lessonAfter = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks?include_archived=true -Headers $lessonHeaders).items
    if (@($lessonAfter | Where-Object { $_.title.StartsWith($lessonPrefix) }).Count -ne 0) { throw '仍有本轮残留' }
    Write-Output "run=$RunName 残留检查完成，本次清理$($lessonTargets.Count)条"
}
```

文件 `exercises/jmeter/archive_smoke.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day06/exercises/jmeter/archive_smoke.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_archive_workflow.jmx -RunName archive06 -BusinessRequests 8
Remove-LessonTasks -RunName archive06
```

文件 `exercises/verify_archive_mutation.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day06/exercises/verify_archive_mutation.py)

```python
from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = "query += \" AND status != 'archived'\""
assert source.count(old) == 1, "请先完成第4天默认过滤实现"
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_archive.py",
        "-k", "default_list", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, 'query += ""', 1), encoding="utf-8")
    assert subprocess.run(args).returncode == 1
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("归档列表泄漏缺陷已检出，源码已恢复")
```

文件 `docs/bug_report_archive.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day06/docs/bug_report_archive.md)

```markdown
# [归档列表] 默认查询泄漏归档任务（主动注入）

需求：缺省include_archived时列表排除archived。
前置：Alice通过API准备open、done、archived各一条。
步骤：去掉默认过滤后GET /tasks。
预期：含本次open/done，不含archived。
注入后行为：SQL仍按owner隔离但未过滤状态，归档ID出现在默认列表。
证据测试：test_default_list_excludes_archived[default/false]。
根因：默认列表SQL遗漏status过滤，结构及HTTP200仍正确，需业务断言发现。
修复：恢复过滤；默认/false排除，true可查；权限、排序、SQL、并行回归。
实际日期、运行输出、JMX/JTL/检查器退出码与报告位置：本人执行后追加。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.verify_archive_mutation
& .\exercises\jmeter\archive_smoke.ps1
```

**对照运行后的结果：** Python故障验证通过；实际JMeter执行应为1线程3轮25成功样本，未运行引擎不能勾选。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 新 JMX 的 25 样本全部成功，列表断言检查当前资源与状态，保留原始结果。
- [ ] 默认列表缺陷有“正常通过→注入失败→恢复通过”的证据，改动已恢复。
- [ ] 报告含最短复现、需求、预期/实际、根因、清理与回归范围。

**卡住时：** 计划增加 sampler 后不能仍用旧 19 样本门槛；有缺样本先定位断言或线程提前停止。

<a id="day-7"></a>

## 第 7 天：现场演示与最终作品包

**材料：** [交付检查](../DELIVERY.md)、[能力验收](../LEARNING_OUTCOMES.md)、[简历与面试](../RESUME_INTERVIEW.md)。

**操作：**

1. 新建 `docs/my_delivery.md`，索引个人贡献、契约/设计、测试命令、SQL、Linux、CI、JMX/JTL/报告、缺陷记录、版本、限制与未完成项。
2. 不看测试答案，演示三件事：done→archived 成功并查到；open→archived 被拒绝且无部分写入；Bob 越权被拒绝。再解释第 6 天测试怎样抓到故障。
3. 按能力验收逐项给出证据位置；缺 Linux/CI/JMeter 执行的项写未完成，补做后才能勾选。
4. 按简历章节整理两分钟项目介绍，只保留自己做过并能复现的条目。最后执行默认回归，确认没有故障注入残留。

```powershell
.\.venv\Scripts\python.exe -m pytest
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

演示脚本完整跑拒绝与成功链路，并在finally回收同ID。交付说明提供可复现命令和贡献边界，所有实际链接/版本/结果用自己的证据补上。

文件 `exercises/archive_demo.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day07/exercises/archive_demo.py)

```python
import os
import requests

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765").rstrip("/")


def login(session, user):
    response = session.post(f"{base}/login", json={"username": user, "password": f"{user}-pass"}, timeout=3)
    assert response.status_code == 200
    session.headers["Authorization"] = "Bearer " + response.json()["token"]


with requests.Session() as alice, requests.Session() as bob:
    alice.trust_env = bob.trust_env = False
    login(alice, "alice")
    login(bob, "bob")
    response = alice.post(f"{base}/tasks", json={"title": "archive-demo"}, timeout=3)
    assert response.status_code == 201
    task = response.json()
    path = f"{base}/tasks/{task['id']}"
    try:
        assert alice.put(path, json={"title": "illegal", "status": "archived"}, timeout=3).status_code == 409
        assert alice.get(path, timeout=3).json() == task
        assert alice.put(path, json={"status": "done"}, timeout=3).status_code == 200
        response = alice.put(path, json={"status": "archived"}, timeout=3)
        assert response.status_code == 200
        assert response.json()["status"] == "archived"
        assert alice.get(path, timeout=3).json()["status"] == "archived"
        assert bob.get(path, timeout=3).status_code == 403
        assert alice.put(path, json={"title": "blocked"}, timeout=3).status_code == 409
        print("归档成功、非法转换无副作用、Bob越权拒绝、title锁定：全部通过")
    finally:
        assert alice.delete(path, timeout=3).status_code in (204, 404)
```

文件 `docs/my_delivery.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/09/day07/docs/my_delivery.md)

```markdown
# 我的归档功能交付说明（参考结构）

个人新增：状态转换/归档锁定、列表过滤、归档HTTP和SQL测试、JMeter归档查询断言。
复用：教程的HTTP/SQLite靶场、APIClient、登录fixture、任务工厂、CI基础结构。
设计：change_archive.md及archive_cases.md；契约：API_CONTRACT.md的归档规则。
运行：python -m pytest tests/workflow/test_archive.py；python -m pytest -n 2。
演示：重启归档版手动服务后python -m exercises.archive_demo。
故障：python -m exercises.verify_archive_mutation；缺陷说明bug_report_archive.md。
SQL：归档成功status落库；409时title/status均保持原值。
清理：工厂按ID删除；JMeter残留使用include_archived=true列表按run_id过滤回收。
JMeter：my_archive_workflow.jmx，1线程3轮25样本，以JTL检查器为门槛。
限制：教学鉴权、SQLite本机同步写、短时同机实验；未证明生产容量。

本人实际代码版本/差异、Windows与Linux报告、CI链接、JTL路径、检查器退出码：执行后填写。
未完成项：据实列出；不能把参考脚本存在写成实际执行通过。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.archive_demo
.\.venv\Scripts\python.exe -B -m pytest tests/workflow -q
```

**对照运行后的结果：** 演示脚本和完整业务回归通过；Linux/CI/JMeter证据齐全后才能判定综合交付完成。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 练习 04 的归档需求、旧功能兼容、权限、原子性、查询/删除都满足。
- [ ] 全部交付证据可打开、可追溯版本；别人按说明能安装与运行。
- [ ] 能现场解释一个需求边界、一个失败根因、一个隔离/清理设计，个人贡献与样例来源明确。

**未通过怎么办：** 用 [交付评分](../DELIVERY.md#评审评分100-分) 找缺口，回到对应学习日补证据。完成本阶段后，可按能力章节另选一个没看过答案的新需求做独立综合考核；那是进一步自测，不用假定本次归档作业已证明所有新需求都能独立处理。
