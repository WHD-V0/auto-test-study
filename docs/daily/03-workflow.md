# 阶段三：让业务测试独立、可清理、可重复

[每日目录](README.md) · [上一阶段](02-http-design.md) · [下一阶段](04-sql.md) · [练习 03](../../exercises/exercise_03_api.md)

本周在 `tests/workflow/test_tasks_extended.py` 继续，不覆盖上周成果。按业务风险统计场景，至少 12 个，其中至少 6 个自己新增；参数化行可算独立输入场景，但不能把只改标题的重复场景充数。每天将用例编号与测试名关联到 `docs/task_cases.md`。

<a id="day-1"></a>

## 第 1 天：独立完成同一资源的 CRUD

**材料：** `test_full_crud`、契约的业务闭环。

**操作：**

1. 自写 `test_my_crud`：用工厂创建 → 保存返回 ID → GET → PUT title/status → GET → DELETE → GET 404。
2. 创建时检查 Schema、owner、初始状态；更新与再查检查新值；删除时用 `delete(..., expect_status=204)` 检查 `content == b''`。
3. 不从其他测试拿 ID，不在模块全局保存资源。由 `task_factory` 负责最终清理，已删资源的 404 应被允许。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py::test_my_crud -vv --tb=short
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

路径只从当前创建响应的 ID 生成；更新响应与再查询都要等于 expected。先删除再查 404，避免把一次删除响应当作数据真的不存在。

文件 `tests/workflow/test_tasks_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/03/day01/tests/workflow/test_tasks_extended.py)

接在第二阶段已有的 extended 文件后；重复的 import 可合并到文件顶部，同名测试只留一个。

```python
import pytest
from core.validator import assert_schema
from tests.workflow.test_tasks import TASK_SCHEMA


def test_my_crud(alice_client, task_factory):
    task = task_factory("my-crud")
    path = f"/tasks/{task['id']}"
    assert_schema(task, TASK_SCHEMA)
    assert task["owner"] == "alice"
    assert task["status"] == "open"
    assert alice_client.get_json(path) == task
    expected = {**task, "title": "changed", "status": "done"}
    assert alice_client.put_json(path, {"title": "changed", "status": "done"}) == expected
    assert alice_client.get_json(path) == expected
    deleted = alice_client.delete(path, expect_status=204)
    assert deleted.content == b""
    assert alice_client.get_json(path, expect_status=404) == {"error": "not_found"}
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py::test_my_crud -q
```

**对照运行后的结果：** 本日新增 1 条闭环测试通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 所有操作针对同一返回 ID，更新/删除均有再查。
- [ ] 单条测试独立通过，能解释每条断言发现哪种错误。
- [ ] 删除使用原始 Response，没有对 204 调用 `.json()`。

**卡住时：** `post_json` 默认期望 201，`put_json/get_json` 默认 200，`delete` 需显式指定 204；查客户端签名，不靠试错改预期。

<a id="day-2"></a>

## 第 2 天：用两个用户验证权限

**材料：** `alice_client`、`bob_client`、`anonymous_client`，本周设计表的权限矩阵。

**操作：**

1. 自写缺失 token 与伪造 token 的创建测试，期望 401，Alice 前后列表不变。
2. Alice 用工厂建资源，Bob 分别 GET/PUT/DELETE 同一 ID，期望 403；每次后由 Alice 再查原值。
3. 三种方法可用参数化，ids 写清方法。不要把 `alice_client` 的 header 改成 Bob 的 token；使用各自独立客户端。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -k 'auth or other_user' -v
```

给自写函数名加上 `auth` 或 `other_user`，确保有测试被选中。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

两组参数化展开成 5 个场景。PUT 才需要 JSON，GET/DELETE 不加无关 body；拒绝后始终由资源主人再查原对象。每条测试都有独立 fixture。

文件 `tests/workflow/test_tasks_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/03/day02/tests/workflow/test_tasks_extended.py)

```python
@pytest.mark.parametrize("token", [None, "invalid-token"], ids=["missing", "invalid"])
def test_auth_missing_or_invalid(anonymous_client, alice_client, token):
    before = alice_client.get_json("/tasks")
    if token is not None:
        anonymous_client.set_token(token)
    result = anonymous_client.post_json("/tasks", {"title": "should-not-exist"}, expect_status=401)
    assert result == {"error": "unauthorized"}
    assert alice_client.get_json("/tasks") == before


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"], ids=["GET", "PUT", "DELETE"])
def test_other_user_access(alice_client, bob_client, task_factory, method):
    task = task_factory("alice-private")
    path = f"/tasks/{task['id']}"
    kwargs = {"json": {"title": "stolen"}} if method == "PUT" else {}
    response = bob_client.request(method, path, expect_status=403, **kwargs)
    assert response.json() == {"error": "forbidden"}
    assert alice_client.get_json(path) == task
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py -k 'auth or other_user' -q
```

**对照运行后的结果：** 本日选中 5 passed，其他日期的测试为 deselected。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 401 与三种 403 场景通过，拒绝后验证无写入或修改。
- [ ] 任意一个权限场景单独运行也通过。
- [ ] 能解释“Bob 的 token 合法，为什么仍是 403”。

**卡住时：** 403 测试先保证资源存在且属于 Alice；随便用一个不存在的 ID 只会测到 404。

<a id="day-3"></a>

## 第 3 天：列表隔离与结构断言

**材料：** 样例 `test_list_is_scoped_to_current_user`、`TASK_SCHEMA`。

**操作：**

1. 工厂分别为 Alice、Bob 建任务：`task_factory(client=bob_client)` 指定 Bob。
2. 分别取列表，校验 `items` 是数组，并对全部元素检查 Schema。
3. 对每个用户检查：自己的刚建 ID 在列表、对方的 ID 不在列表、所有元素 owner 正确、ID 升序。
4. 再补一个“先有任务 → 删除 → 列表不再含该 ID”的场景。不要假定整个 session 数据库始终只有这一条记录。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -k list -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

列表必须逐元素验证 owner 和 Schema；自己/对方 ID 的断言证明该测试准备的数据被正确隔离。排序比较只检查 ID 序列，不假定全库条数固定。

文件 `tests/workflow/test_tasks_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/03/day03/tests/workflow/test_tasks_extended.py)

```python
def test_list_user_isolation(alice_client, bob_client, task_factory):
    alice_task = task_factory("alice-list")
    bob_task = task_factory("bob-list", client=bob_client)
    for client, owner, own, other in [
        (alice_client, "alice", alice_task, bob_task),
        (bob_client, "bob", bob_task, alice_task),
    ]:
        items = client.get_json("/tasks")["items"]
        assert_schema(items, {"type": "array", "items": TASK_SCHEMA})
        ids = [item["id"] for item in items]
        assert own["id"] in ids
        assert other["id"] not in ids
        assert all(item["owner"] == owner for item in items)
        assert ids == sorted(ids)


def test_list_excludes_deleted_task(alice_client, task_factory):
    task = task_factory("will-delete")
    alice_client.delete(f"/tasks/{task['id']}", expect_status=204)
    items = alice_client.get_json("/tasks")["items"]
    assert task["id"] not in [item["id"] for item in items]
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py -k list -q
```

**对照运行后的结果：** 本日列表测试 2 passed。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 列表断言覆盖每个元素，包含自己且排除他人，删除后无该 ID。
- [ ] 能说明只检查第一条、只检查列表非空各遗漏什么风险。
- [ ] 修改测试中的预期 owner 会失败，恢复后通过。

**卡住时：** 不依赖固定列表长度；使用本测试工厂返回的 ID 比较。

<a id="day-4"></a>

## 第 4 天：验证断言失败后仍清理已创建资源

**材料：** `task_factory` 中 `created.append`、`yield` 及清理循环。

**操作：**

1. 用自己的话写出：成功创建 → 立即登记 → 测试断言 → yield 后回收。把登记放在断言之后会有什么问题？
2. 在 extended 文件临时加下列测试；测试名中的 `cleanup_probe` 方便单独运行：

```python
def test_cleanup_probe(task_factory):
    task_factory("cleanup-probe")
    assert False, "仅用于验证失败后的清理，实验后删除此测试"
```

3. 在本地 `tests/workflow/conftest.py` 的 `task_factory` 清理循环中，紧接 DELETE 之后、同一个 try 块内临时加入下面两行；这里的 `client`、`task_id` 都来自清理循环：

```python
assert client.get_json(f"/tasks/{task_id}", expect_status=404) == {"error": "not_found"}
print("cleanup verified", task_id)
```

4. 用 `-s --setup-show` 观察目标断言失败，但 teardown 的 GET 404 验证成功并打印该 ID。保存输出后删除故意失败的 `test_cleanup_probe`，将公共 fixture 中临时加的两行恢复，运行自己的正常测试文件。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -k cleanup_probe -v -s --setup-show
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

清理循环先 DELETE，再 GET 404，最后打印 verified。故意失败文件只用于本日实验，不永久留在 tests；明天的恢复代码会还原工厂并删除探针。

文件 `tests/workflow/conftest.py` — 只替换函数 task_factory（含装饰器），保留文件其余部分。 [打开参考文件](reference/03/day04/tests/workflow/conftest.py)

仅替换该文件原来的 task_factory 函数（含装饰器）；其他 fixture 和文件顶部 import 保留。

```python
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
            assert client.get_json(f"/tasks/{task_id}", expect_status=404) == {"error": "not_found"}
            print("cleanup verified", task_id)
        except Exception as exc:
            errors.append(f"task {task_id}: {exc}")
    if errors:
        pytest.fail("资源清理失败: " + "; ".join(errors))
```

文件 `tests/workflow/test_cleanup_probe.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/03/day04/tests/workflow/test_cleanup_probe.py)

```python
def test_cleanup_probe(task_factory):
    task_factory("cleanup-probe")
    assert False, "故意失败，用于观察teardown；实验结束删掉本文件"
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
# 故意失败实验，预期退出码 1；核对下面的结果说明。
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_cleanup_probe.py -q -s
```

**对照运行后的结果：** 1 failed 属于预期，同时必须出现 cleanup verified；不得出现 teardown ERROR。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 故意失败发生在创建之后；teardown 通过 GET 404 验证资源确实消失。
- [ ] 记录目标失败与清理结果，恢复后文件中的正常测试通过。
- [ ] 能解释登记时机、清理允许 404、清理网络错误不能吞掉。

**卡住时：** 清理发生在同一测试进程结束前，用清理循环中的再查验证；另开一次 pytest 会创建新库，不能证明上次是否已清理。

<a id="day-5"></a>

## 第 5 天：补边界、未知字段、非法 JSON 与原子性

**材料：** 练习 03 的实现要求，样例 `test_invalid_update_is_atomic`。

**操作：**

1. 检查自己的用例覆盖 title 长度 1/80/81、首尾空白、错误类型，补缺项。
2. 增加原子性测试：建 `before/open` → PUT 合法 title 加非法 status → 400 → GET 仍为完整原对象。
3. 增加未知字段测试，POST 或 PUT 带 owner/id 应 400，核对列表或原资源未变。
4. 增加非法 JSON 测试，用 `client.request('POST', '/tasks', data='{', headers={'Content-Type': 'application/json'}, expect_status=400)`；再断言 health 可用、列表不变。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -v --tb=short
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

先删掉昨天的故意失败探针并恢复清理工厂，再追加本日场景。title 81 与 80 成对；原子性用整个旧对象比较，防止只检查 status 而遗漏 title 已被写入。

删除实验文件 `tests/workflow/test_cleanup_probe.py`（只删除这一个文件；正常代码保留）：

```powershell
Remove-Item -LiteralPath tests/workflow/test_cleanup_probe.py
```

文件 `tests/workflow/conftest.py` — 只替换函数 task_factory（含装饰器），保留文件其余部分。 [打开参考文件](reference/03/day05/tests/workflow/conftest.py)

恢复昨天临时修改的工厂；保留其余内容。

```python
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
```

文件 `tests/workflow/test_tasks_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/03/day05/tests/workflow/test_tasks_extended.py)

```python
@pytest.mark.parametrize("title", ["x", "x" * 80, "  normalized  "], ids=["min", "max", "trim"])
def test_title_boundaries(alice_client, task_factory, title):
    task = task_factory(title)
    assert task["title"] == title.strip()
    assert_schema(task, TASK_SCHEMA)
    assert alice_client.get_json(f"/tasks/{task['id']}") == task


@pytest.mark.parametrize("title", ["x" * 81, "   ", None, 123], ids=["too-long", "blank", "null", "number"])
def test_title_invalid(alice_client, title):
    before = alice_client.get_json("/tasks")
    result = alice_client.post_json("/tasks", {"title": title}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before


def test_invalid_update_is_atomic_extended(alice_client, task_factory):
    task = task_factory("before")
    path = f"/tasks/{task['id']}"
    result = alice_client.put_json(path, {"title": "changed", "status": "unknown"}, expect_status=400)
    assert result == {"error": "invalid_fields"}
    assert alice_client.get_json(path) == task


@pytest.mark.parametrize("field,value", [("owner", "bob"), ("id", 9)])
def test_unknown_fields_extended(alice_client, field, value):
    before = alice_client.get_json("/tasks")
    alice_client.post_json("/tasks", {"title": "protected", field: value}, expect_status=400)
    assert alice_client.get_json("/tasks") == before


def test_invalid_json_extended(alice_client):
    before = alice_client.get_json("/tasks")
    response = alice_client.request("POST", "/tasks", data="{",
        headers={"Content-Type": "application/json"}, expect_status=400)
    assert response.json() == {"error": "invalid_json_object"}
    assert alice_client.get_json("/health") == {"status": "ok"}
    assert alice_client.get_json("/tasks") == before
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/workflow/test_tasks_extended.py -q
```

**对照运行后的结果：** 第三阶段从零累计为 19 条；若保留第二阶段两条则为 21 条，全部通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 规则与输入一一对应，失败场景有副作用断言，非法 JSON 后服务仍健康。
- [ ] 至少 12 个有明确风险的场景；至少 6 个自写，表中标明与样例的关系。
- [ ] 能解释“PUT 返回 400”为什么还不能证明没有部分写入。

**卡住时：** 非法 JSON 用 `data='{'`，不要 `json={'title': '{'}`；后者是合法 JSON 字符串字段。

<a id="day-6"></a>

## 第 6 天：单独、重复、换顺序、并行运行

**材料：** `tests/workflow/conftest.py` 中动态端口、`local_api_db`、function 客户端。

**操作与运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py::test_my_crud -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -v
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -n 2
```

再从 `--collect-only -q` 复制自己的两个完整 nodeid，先 A B、再 B A 作为命令的两个位置参数执行；参数化 nodeid 用引号包住。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

这是把本日六种运行方式写成可重复执行的脚本。check=True 遇到失败立即暴露，不继续打印“全部通过”；没有自动重试。脚本本身不复制 ID 或共享 token。

文件 `exercises/check_workflow_independence.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/03/day06/exercises/check_workflow_independence.py)

```python
import subprocess
import sys

module = "tests/workflow/test_tasks_extended.py"
a = module + "::test_my_crud"
b = module + "::test_list_user_isolation"
runs = [[a], [module], [module], [a, b], [b, a], [module, "-n", "2"]]
for args in runs:
    print("RUN", " ".join(args), flush=True)
    subprocess.run([sys.executable, "-B", "-m", "pytest", *args, "-q"], check=True)
print("单独、重复、交换顺序、双worker：全部通过")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.check_workflow_independence
```

**对照运行后的结果：** 六次运行均退出 0，最后打印全部通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 单独、两次连续、两个顺序、两个 worker 均通过，有命令与退出码记录。
- [ ] 解释为什么每个 worker 的 session fixture 会得到自己的端口/库。
- [ ] 没有固定 ID、跨测试 token 或依赖前一测试创建数据。

**卡住时：** 单跑通过、一起失败先查共享状态；并行失败先查固定端口/共享文件，不先加重试。

<a id="day-7"></a>

## 第 7 天：用越权缺陷验证测试，再交付

**材料：** `sandbox/task_api.py` 中 owner 权限判断；[排障指南](../DEBUGGING.md)。

**操作：**

1. 先记录正常权限测试通过。在 `sandbox/task_api.py` 找到 `if row["owner"] != username:`，只对这一处让越权检查暂时失效；记住原始代码。
2. 跑自己第 2 天的 Bob GET/PUT/DELETE 测试，预期至少一条在“期望 403”处失败；语法错误不算发现越权。
3. 恢复那一处，跑自己的文件与整个 workflow，再更新设计表、学习记录。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -k other_user -v
.\.venv\Scripts\python.exe -m pytest tests/workflow -n 2
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

脚本先跑正常基线，再暂时禁用 owner 检查，最后恢复并重跑。Bob DELETE 的缺陷实验可能导致主人再查 404，这也属于越权造成的数据破坏；最终必须恢复权限，不能保留缺陷。

文件 `exercises/verify_owner_mutation.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/03/day07/exercises/verify_owner_mutation.py)

```python
from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = 'if row["owner"] != username:'
assert source.count(old) == 1
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_tasks_extended.py",
        "-k", "other_user", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, "if False:", 1), encoding="utf-8")
    result = subprocess.run(args)
    assert result.returncode == 1, "移除权限判断后，应在期望403处失败"
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("越权缺陷已捕获；源码恢复，权限回归通过")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.verify_owner_mutation
```

**对照运行后的结果：** 正常3 passed → 注入后权限场景失败 → 恢复后3 passed，脚本最终退出0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 有至少 12 个场景、至少 6 个新增、设计映射和清理证据。
- [ ] 越权缺陷有“通过→失败→恢复通过”记录；源代码已恢复。
- [ ] 能独立解释一个正常闭环、一个拒绝场景、一个并行隔离设计。

**未通过怎么办：** 只断言状态码回第 1/5 天；清理不确定回第 4 天；不稳定回第 6 天。
