# 阶段二：先知道应该怎样，再发送请求

[每日目录](README.md) · [上一阶段](01-python-pytest.md) · [下一阶段](03-workflow.md)

本周交付 `docs/task_cases.md`、手工验证记录和第一条自写 HTTP 测试。命令为 PowerShell。手动服务使用固定端口；pytest 自己启动另一份临时服务，两者的数据互不相通。

<a id="day-1"></a>

## 第 1 天：启动服务，看清一条 HTTP 请求

**材料：** [接口契约](../API_CONTRACT.md) 的运行方式、端点表和任务结构。

**操作：**

1. 开两个项目根目录终端。终端 A 执行下面服务命令并保持运行；终端 B 发健康请求：

```powershell
# 终端 A
.\.venv\Scripts\python.exe -m sandbox.task_api --port 8765 --db reports/learning/manual-tasks.sqlite3
```

```powershell
# 终端 B
$lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
$lessonHealth.StatusCode
$lessonHealth.Headers['Content-Type']
$lessonHealth.Content
```

2. 记录 method=GET、scheme=http、host=127.0.0.1、port=8765、path=/health，预期状态 200、正文 `{"status":"ok"}`。
3. 在 `docs/task_cases.md` 写出 `/login` 与 `/tasks` 的方法、必填字段、成功码；给 query（URL 中 `?` 后的参数）、JSON body、headers 各写一句用途。当前任务列表没有分页参数，不给它杜撰 `page` 需求。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

保持原来的终端 A 服务运行，终端 B 用下方模块运行命令执行 Python 版本。Session 的 with 负责关闭连接；trust_env=False 只针对本机教学地址。默认地址可通过 LESSON_BASE_URL 改成测试服务地址。

文件 `exercises/http_day01.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day01/exercises/http_day01.py)

```python
import os
import requests

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765")
with requests.Session() as session:
    session.trust_env = False  # 本机实验不经过系统代理。
    response = session.get(f"{base}/health", timeout=3)
    print("status:", response.status_code)
    print("content-type:", response.headers.get("Content-Type"))
    print("body:", response.json())
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

文件 `docs/http_notes.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day01/docs/http_notes.md)

```markdown
# HTTP 请求记录（参考写法）

| 项目 | health 请求 | 登录请求 | 创建任务请求 |
|---|---|---|---|
| method | GET | POST | POST |
| path | /health | /login | /tasks |
| JSON body | 无 | username/password | title |
| headers | 无需认证 | Content-Type: application/json | JSON 及 Authorization: Bearer token |
| 预期状态 | 200 | 200 | 201 |
| 预期业务 | status=ok | 获得 token、username | 正整数 ID，owner=alice，status=open |

URL 的 query 是 ? 后的参数，例如后续归档需求的 include_archived=true。
JSON body 承载结构化输入；header 承载内容类型与身份等元信息。
本阶段 /tasks 没有分页需求，不能自行约定 page 的服务端行为。
执行日期、实际状态及证据：由本人运行后填写，不把此表当已执行记录。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.http_day01
```

**对照运行后的结果：** 打印 status: 200、JSON 内容类型、body: {'status': 'ok'}，脚本退出 0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 亲自看到 health 的状态、响应头、正文，能分清这三部分。
- [ ] 能解释 POST 创建是 201、DELETE 成功是 204、查到资源是 200，依据来自契约。
- [ ] 能指出终端 A 是服务，终端 B 是客户端；终端 A 保持运行时仍能在 B 操作。

**卡住时：** 连接拒绝先看终端 A 是否报错、端口是否一致；端口占用按 [Linux/排障材料](../DEBUGGING.md) 的思路找占用者，不随意结束所有 Python。

<a id="day-2"></a>

## 第 2 天：登录、创建、查询、删除同一资源

**材料：** 接口契约的鉴权和业务闭环。沿用昨天终端 A 的服务、终端 B 的 PowerShell。

**操作：** 在终端 B 逐条运行，先猜每一步的状态和正文，再核对：

```powershell
$lessonLogin = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/login -ContentType 'application/json' -Body '{"username":"alice","password":"alice-pass"}'
$lessonHeaders = @{ Authorization = "Bearer $($lessonLogin.token)" }
$lessonCreate = Invoke-WebRequest -UseBasicParsing -Method Post -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders -ContentType 'application/json' -Body '{"title":"manual-day02"}'
$lessonCreate.StatusCode
$lessonTask = $lessonCreate.Content | ConvertFrom-Json
$lessonTask
$lessonPath = "http://127.0.0.1:8765/tasks/$($lessonTask.id)"
Invoke-RestMethod -Uri $lessonPath -Headers $lessonHeaders
$lessonDeleted = Invoke-WebRequest -UseBasicParsing -Method Delete -Uri $lessonPath -Headers $lessonHeaders
$lessonDeleted.StatusCode
$lessonDeleted.RawContentLength
```

1. 检查创建状态为 201、owner=alice、status=open；查询 ID 与刚创建的一致。
2. 检查删除状态为 204，正文长度为 0。不要对空响应执行 JSON 解析。
3. 再发一次查询，PowerShell 会因 404 报错，这是预期的 HTTP 错误。保留状态码即可，不把 token 复制到学习记录。
4. 在记录中解释 401（没认证）、403（认证了但不准访问）、404、409（规则冲突）、5xx。当前 open/done 功能没有归档冲突，409 留到阶段九实作。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

两个文件都要保存：manual_http 提供登录和显式状态检查，http_day02 使用它。finally 在业务断言失败时也回收本次登记的 ID，清理允许资源已删除的 404。状态码和字段都对才通过。

文件 `exercises/manual_http.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day02/exercises/manual_http.py)

```python
import os
import requests

BASE = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765").rstrip("/")


def login(username="alice"):
    session = requests.Session()
    session.trust_env = False
    try:
        response = session.post(f"{BASE}/login", json={
            "username": username, "password": f"{username}-pass"}, timeout=3)
        assert response.status_code == 200
        session.headers["Authorization"] = "Bearer " + response.json()["token"]
        return session
    except Exception:
        session.close()
        raise


def checked(session, method, path, expected, **kwargs):
    response = session.request(method, f"{BASE}{path}", timeout=3, **kwargs)
    assert response.status_code == expected, (method, path, expected, response.status_code)
    return response
```

文件 `exercises/http_day02.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day02/exercises/http_day02.py)

```python
from exercises.manual_http import BASE, login, checked

with login() as session:
    task_id = None
    try:
        created = checked(session, "POST", "/tasks", 201, json={"title": "manual-day02"})
        task = created.json()
        task_id = task["id"]  # 在后面的断言前登记，失败时也可清理。
        path = f"/tasks/{task_id}"
        assert task["owner"] == "alice"
        assert task["status"] == "open"
        assert checked(session, "GET", path, 200).json() == task
        deleted = checked(session, "DELETE", path, 204)
        assert deleted.content == b""
        assert checked(session, "GET", path, 404).json() == {"error": "not_found"}
        print("201 → 200 → 204 → 404，同一资源闭环通过")
    finally:
        if task_id is not None:
            response = session.delete(f"{BASE}/tasks/{task_id}", timeout=3)
            assert response.status_code in (204, 404)
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.http_day02
```

**对照运行后的结果：** 脚本打印 201 → 200 → 204 → 404，退出 0；本次 ID 不留在库中。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 同一个返回 ID 完成创建→查→删→404，没有写死 ID。
- [ ] 能指出 JSON body 在创建请求里，Authorization 在请求头里，二者用途不同。
- [ ] 能说出“HTTP 4xx”与“连不上服务”的区别。

**卡住时：** 新开 B 终端后变量会丢失，需重新登录；不要把示例的字面 `<token>` 作为真实 token。

<a id="day-3"></a>

## 第 3 天：用等价类和边界表设计输入

**材料：** [用例设计](../TEST_DESIGN.md) 的 TASK-06/07/08/10/13，练习 03 的设计部分。

**操作：**

1. 在 `docs/task_cases.md` 写表，列：编号、需求依据、风险、前置、输入、预期状态、业务值/副作用、清理方式、优先级、自动化测试名（未写可留空）。
2. 先写至少六条输入场景：title 长度 1、80、81、全空白、数字、首尾空白。明确长度按去掉首尾空白后的 Python Unicode 字符数计算。
3. 为错误输入写“400，创建前后列表不变”，为正确输入写“201，查询值正确”。只写“失败”不够。
4. 手动试两条：`$lessonHeaders` 沿用第 2 天登录；合法请求用 `Invoke-RestMethod`；非法请求使用下面形式取得状态。合法创建后用其 ID 删除。

```powershell
try {
    Invoke-WebRequest -UseBasicParsing -Method Post -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders -ContentType 'application/json' -Body '{"title":"   "}'
} catch {
    [int]$_.Exception.Response.StatusCode
}
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

每个 tuple 都先写预期，再发送请求。成功分支校验归一化及再查询，失败分支校验未创建；finally 仅删除本轮创建的 ID。表格是可交付写法，执行状态需用自己的证据补上。

文件 `exercises/http_day03.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day03/exercises/http_day03.py)

```python
from exercises.manual_http import BASE, login, checked

cases = [
    ("one", "x", 201), ("max", "x" * 80, 201), ("too-long", "x" * 81, 400),
    ("blank", "   ", 400), ("number", 123, 400), ("trim", "  hello  ", 201),
]
with login() as session:
    for name, title, expected in cases:
        before = checked(session, "GET", "/tasks", 200).json()
        task_id = None
        try:
            response = checked(session, "POST", "/tasks", expected, json={"title": title})
            if expected == 201:
                task = response.json()
                task_id = task["id"]
                assert task["title"] == title.strip()
                assert checked(session, "GET", f"/tasks/{task_id}", 200).json() == task
            else:
                assert response.json() == {"error": "invalid_fields"}
                assert checked(session, "GET", "/tasks", 200).json() == before
            print(name, expected, "PASS")
        finally:
            if task_id is not None:
                assert session.delete(f"{BASE}/tasks/{task_id}", timeout=3).status_code in (204, 404)
```

文件 `docs/task_cases.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day03/docs/task_cases.md)

```markdown
# 我的任务用例表（参考成品；执行状态需本人填写）

| 编号 | 需求/风险 | 前置/输入 | 预期状态与业务/副作用 | 清理 | 优先级 | 对应测试 |
|---|---|---|---|---|---|---|
| C01 | 最小合法长度 | Alice；title='x' | 201；再查 title=x、owner=alice、status=open | 工厂按 ID 删 | P1 | test_title_boundaries[min] |
| C02 | 最大合法长度 | Alice；80 字符 | 201；再查长度80 | 工厂按 ID 删 | P1 | test_title_boundaries[max] |
| C03 | 超长 | Alice；81 字符 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[too-long] |
| C04 | 全空白 | Alice；三个空格 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[blank] |
| C05 | 错误类型 | Alice；title=123 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_invalid_title_number |
| C06 | 首尾空白 | Alice；title='  hello  ' | 201；再查为hello | 工厂按 ID 删 | P1 | test_title_boundaries[trim] |
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.http_day03
```

**对照运行后的结果：** 六个 case 各打印 PASS，脚本为 0；非法输入前后列表相等。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 至少六行预期在执行前写好，合法/非法边界成对出现。
- [ ] 两条手工结果与预期逐项核对，有创建数据的场景已清理。
- [ ] 能解释“空字符串、null、字段缺失”为什么是不同输入。

**卡住时：** PowerShell 报错不自动证明服务缺陷；先看它是否是自己预期的 400。规范与实现不一致时先记录差异。

<a id="day-4"></a>

## 第 4 天：把权限和副作用补进至少 12 条用例

**材料：** 用例设计的 TASK-02/03/04/05/10/11/12。

**操作：**

1. 扩充昨天的表到至少 12 条；补无 token、无效 token、Bob 读/改/删 Alice 的任务、两个用户列表隔离、更新原子性、非法 JSON。权限的不同方法可分行，不能只测读。
2. 画权限矩阵：匿名/Alice/Bob × 创建、读 Alice 任务、改 Alice 任务、删 Alice 任务、列表。为每格写状态或可见范围。
3. 复核每个拒绝场景：谁来重新查询，怎样证明没改变数据？例如 Bob PUT 被拒绝后由 Alice 查原值。
4. 给每条用例标“已有样例/计划新增/待需求确认”，未知行为列问题，不能照着当前返回值猜规则。

**检查方式：** 对照 `docs/API_CONTRACT.md` 逐条核对表格，今天不以 pytest 数量验收。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

今天交付的是设计文档，所以上面给出完整的 15 条用例及权限矩阵，包含昨天六条输入场景。每条拒绝场景都写明用谁重新查询以验证数据没变。

文件 `docs/task_cases.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day04/docs/task_cases.md)

```markdown
# 我的任务用例表（参考成品；执行状态需本人填写）

| 编号 | 需求/风险 | 前置/输入 | 预期状态与业务/副作用 | 清理 | 优先级 | 对应测试 |
|---|---|---|---|---|---|---|
| C01 | 最小合法长度 | Alice；title='x' | 201；再查 title=x、owner=alice、status=open | 工厂按 ID 删 | P1 | test_title_boundaries[min] |
| C02 | 最大合法长度 | Alice；80 字符 | 201；再查长度80 | 工厂按 ID 删 | P1 | test_title_boundaries[max] |
| C03 | 超长 | Alice；81 字符 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[too-long] |
| C04 | 全空白 | Alice；三个空格 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[blank] |
| C05 | 错误类型 | Alice；title=123 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_invalid_title_number |
| C06 | 首尾空白 | Alice；title='  hello  ' | 201；再查为hello | 工厂按 ID 删 | P1 | test_title_boundaries[trim] |
| C07 | 无 token | 匿名POST title=x | 401 unauthorized；Alice列表不变 | 不应创建 | P0 | test_auth_missing_or_invalid[missing] |
| C08 | 假 token | 伪造Bearer token创建 | 401 unauthorized；列表不变 | 不应创建 | P0 | test_auth_missing_or_invalid[invalid] |
| C09 | 越权读取 | Alice建；Bob GET同ID | 403 forbidden；Alice仍可查原值 | Alice工厂 | P0 | test_other_user_access[GET] |
| C10 | 越权更新 | Alice建；Bob PUT title=stolen | 403；Alice查原值不变 | Alice工厂 | P0 | test_other_user_access[PUT] |
| C11 | 越权删除 | Alice建；Bob DELETE | 403；Alice仍查到原资源 | Alice工厂 | P0 | test_other_user_access[DELETE] |
| C12 | 列表隔离 | 两用户各建任务 | 各自列表含自己、不含对方且所有owner正确 | 各用户工厂 | P0 | test_list_user_isolation |
| C13 | 更新原子性 | before/open；PUT新title+非法status | 400；再查仍为before/open | 工厂 | P1 | test_invalid_update_is_atomic_extended |
| C14 | 非法JSON | POST data='{' | 400 invalid_json_object；health正常、列表不变 | 不应创建 | P1 | test_invalid_json_extended |
| C15 | 字段保护 | POST title=x,owner=bob | 400；无新任务 | 不应创建 | P0 | test_unknown_fields_extended |

## 权限矩阵（Alice 已创建资源）

| 身份 | 创建 | GET Alice任务 | PUT Alice任务 | DELETE Alice任务 | 列表 |
|---|---|---|---|---|---|
| 匿名 | 401 | 401 | 401 | 401 | 401 |
| Alice | 201 | 200 | 200（合法输入） | 204 | 仅Alice，按ID升序 |
| Bob | 201（归属Bob） | 403 | 403 | 403 | 仅Bob，按ID升序 |

以上行为多数已有教程样例；自己实现时标注复用/新增。未约定：分页、并发更新和幂等机制，先确认需求再扩展。
```

**对照运行后的结果：** 用例表15行，矩阵3种身份；每行有前置、输入、明确预期、清理、优先级与追溯测试。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 至少 12 条完整用例，正常、边界、认证、越权、失败副作用都有覆盖。
- [ ] 读、写、删、列表权限都有独立预期；有清理方式和优先级理由。
- [ ] 能说明为什么“带着 token 请求成功”不能证明越权保护有效。

**卡住时：** 同一输入换十个标题不能替代十个风险；优先补遗漏的权限与原子性。

<a id="day-5"></a>

## 第 5 天：亲自验证任务持久化与 token 生命周期

**材料：** 契约的运行与数据、TASK-15。

**操作：**

1. 用第 2 天登录命令重新取得 `$lessonHeaders`，创建标题 `manual-restart` 的任务，保存 `$lessonTask`、`$lessonPath`。今天先别删除它。把 `$lessonHeaders` 赋给 `$lessonOldHeaders` 保留旧 token。
2. 在终端 A 按 Ctrl+C 停服，再用第 1 天**完全相同的数据库路径**启动。B 终端保持打开。
3. 使用旧 headers 查询该 ID，用第 3 天的 try/catch 形式确认 401；重新登录更新 `$lessonHeaders`，再查同一 ID，应能看到原任务。
4. 删除本次任务并确认 404。在记录中写出数据库路径、重启前后 ID、旧 token 状态和新登录后的字段结果，隐藏 token 值。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

手工 Ctrl+C 重启做完后，可以用这份代码对照完整过程。它用同一个临时 SQLite 文件启动两个不同服务实例，不依赖 8765；stop 会等待线程结束，旧实例 token 不会转移到新实例。

文件 `exercises/restart_demo.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day05/exercises/restart_demo.py)

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import requests
from sandbox.task_api import create_server


def start(db_path):
    server = create_server(db_path)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def stop(server, thread):
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


def token(session, base):
    response = session.post(f"{base}/login", json={"username": "alice", "password": "alice-pass"}, timeout=3)
    assert response.status_code == 200
    return {"Authorization": "Bearer " + response.json()["token"]}


with TemporaryDirectory() as directory, requests.Session() as session:
    session.trust_env = False
    db = Path(directory) / "persist.sqlite3"
    server, thread, base = start(db)
    try:
        old_headers = token(session, base)
        response = session.post(f"{base}/tasks", headers=old_headers, json={"title": "restart-check"}, timeout=3)
        assert response.status_code == 201
        task = response.json()
    finally:
        stop(server, thread)
    # 端口可以不同；关键是同一个数据库文件，且服务实例已换新。
    server, thread, base = start(db)
    try:
        path = f"{base}/tasks/{task['id']}"
        assert session.get(path, headers=old_headers, timeout=3).status_code == 401
        new_headers = token(session, base)
        response = session.get(path, headers=new_headers, timeout=3)
        assert response.status_code == 200
        assert response.json() == task
        assert session.delete(path, headers=new_headers, timeout=3).status_code == 204
        print("旧token=401；新登录后同ID任务仍在；已清理")
    finally:
        stop(server, thread)
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.restart_demo
```

**对照运行后的结果：** 脚本验证旧 token=401、新 token 下原 ID/字段完全一致，清理任务后退出 0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 亲眼验证任务重启后保留、旧 token 失效、新登录后可查。
- [ ] 能解释“创建响应回显标题”为什么不足以证明持久化。
- [ ] 明确更换数据库路径会换数据集，不能用它验证同一库的重启持久化。

**卡住时：** 不要用 pytest 临时数据库的结果寻找手动任务；端口相同不代表数据库相同。

<a id="day-6"></a>

## 第 6 天：把一次手工验证改成自动测试

**材料：** `tests/workflow/conftest.py` 中 `alice_client`、`task_factory`；`tests/workflow/test_tasks.py::test_full_crud`。

**操作：**

1. 新建 `tests/workflow/test_tasks_extended.py`，先理解下面的创建与再查，再对照本日完整代码检查全部 import、Schema 和业务断言：

```python
def test_created_task_can_be_read(alice_client, task_factory):
    task = task_factory("my-first-http-test")
    assert task["owner"] == "alice"
    assert task["status"] == "open"
    actual = alice_client.get_json(f"/tasks/{task['id']}")
    assert actual == task
```

2. `task_factory` 使用实际 HTTP 创建并登记清理；`alice_client` 已登录；创建的 201、查询的 200 由客户端检查。读源码找到这两个检查点。
3. 对返回任务调用 `assert_schema` 和样例的 `TASK_SCHEMA`，再保留业务值断言。Schema 可从 `tests.workflow.test_tasks` 导入用于练习。
4. 停止手动服务也应能跑下面测试，证明它使用 fixture 的动态端口。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py::test_created_task_can_be_read -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

这是原来骨架应补成的完整版本，包括全部 import、Schema 和再查断言。task_factory 通过 POST 创建并检查 201，get_json 默认检查 200；工厂负责清理，无需手动服务。

文件 `tests/workflow/test_tasks_extended.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day06/tests/workflow/test_tasks_extended.py)

```python
from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def test_created_task_can_be_read(alice_client, task_factory):
    task = task_factory("my-first-http-test")
    assert_schema(task, TASK_SCHEMA)
    assert task["owner"] == "alice"
    assert task["status"] == "open"
    actual = alice_client.get_json(f"/tasks/{task['id']}")
    assert_schema(actual, TASK_SCHEMA)
    assert actual == task
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py -q
```

**对照运行后的结果：** 自己的 extended 文件 1 passed；停止终端 A 的手动服务后仍通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 同一资源的创建与查询、Schema、owner 和 status 均有断言。
- [ ] 手动服务停止后测试通过；不含写死的 token、ID 或 8765。
- [ ] 能指出哪一步验证 HTTP、结构、业务值，哪一处负责清理。

**卡住时：** 放到 `tests/` 顶层会找不到这里的 fixture；不要在测试中再手动启动服务器。

<a id="day-7"></a>

## 第 7 天：评审设计并独立加一个异常测试

**操作：**

1. 合上样例，在自己的 extended 文件增加一个 title 为数字时创建失败的测试：创建前 GET 列表、POST 期望 400、断言错误码和列表不变。
2. 给它与昨天的测试对应上设计表编号；重新审查 12 条用例是否每行有明确预期和数据清理。
3. 运行自己的文件与现有基线：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

追加异常函数即可，不需要新的 import。比较完整前后列表，验证的是拒绝写入的副作用。复习记录演示如何解释测试意义；最后一项必须使用自己的运行证据。

文件 `tests/workflow/test_tasks_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/02/day07/tests/workflow/test_tasks_extended.py)

```python
def test_invalid_title_number(alice_client):
    before = alice_client.get_json("/tasks")
    result = alice_client.post_json("/tasks", {"title": 123}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    after = alice_client.get_json("/tasks")
    assert after == before
```

文件 `docs/week02_review.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/02/day07/docs/week02_review.md)

```markdown
# 第二周复习记录写法

- 401：缺失或无效身份；403：Bob身份有效但无权访问Alice的任务。
- 204：成功且响应体为空，用原始Response检查，不解析JSON。
- Schema：检查字段/类型；业务断言：核对owner、状态和实际值；副作用断言：失败后列表或原资源不变。
- 我写的正常场景：test_created_task_can_be_read，对应创建/再查与归属规则。
- 我写的异常场景：test_invalid_title_number，对应C05。
- 设计表：C01—C15；剩余自动化将在第三阶段完成。
- 实际运行命令、日期、输出与重启记录：本人执行后追加。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py -q
```

**对照运行后的结果：** extended 文件累计 2 passed，用例表与两个测试名对应。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两个自写场景通过，能在设计表找到对应需求与风险。
- [ ] 至少 12 条用例、权限矩阵、重启持久化记录均齐全。
- [ ] 口头解释：401/403、204 不解析 JSON、结构正确与业务正确的区别。

**未通过怎么办：** HTTP 组成不清回第 1—2 天；预期靠猜回第 3—4 天；fixture 不清回第 6 天。进入阶段三时沿用自己的 extended 文件。
