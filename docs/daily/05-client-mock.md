# 阶段五：理解客户端封装、Mock 与失败证据

[每日目录](README.md) · [上一阶段](04-sql.md) · [下一阶段](06-linux.md) · [练习 02](../../exercises/exercise_02_mock.md)

本周新增 `tests/test_client_extended.py`；它属于离线客户端测试，不使用 workflow fixture。测试中的 `https://client.test` 仅是 Mock 地址，每个涉及该地址的测试都必须有 `@responses.activate` 并注册响应。不要真的向它请求。使用的客户端是 `core/api_client.py`，注意项目另有入门样例 `src/api_client.py`。

<a id="day-1"></a>

## 第 1 天：先直接用 requests，再看封装解决什么

**材料：** `core/api_client.py` 的 `request`、`close`、JSON 辅助方法。

**操作：**

1. 如阶段二一样在终端 A 启动手动服务；终端 B 运行下面直接请求，观察状态和 JSON：

```powershell
.\.venv\Scripts\python.exe -c "import requests; r=requests.get('http://127.0.0.1:8765/health', timeout=3); print(r.status_code, r.json())"
```

2. 新建 `exercises/client_compare.py`，用 `with APIClient('http://127.0.0.1:8765', max_retries=0) as client:` 查询 health；因为要导入项目 core，用模块方式运行。
3. 对照两种写法，在学习记录列出 base_url、timeout、状态校验、Session 关闭分别在哪里处理。不要增加一层相同包装。

```powershell
.\.venv\Scripts\python.exe -m exercises.client_compare
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

两种写法都明确超时并关闭Session；APIClient额外集中URL拼接、状态检查和日志。不要把封装当作能自动判断所有业务值的工具，业务预期仍由assert表达。

文件 `exercises/client_compare.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day01/exercises/client_compare.py)

```python
import os
import requests
from core.api_client import APIClient

base = os.environ.get("LESSON_BASE_URL", "http://127.0.0.1:8765")
with requests.Session() as session:
    session.trust_env = False
    response = session.get(f"{base}/health", timeout=3)
    assert response.status_code == 200
    direct = response.json()
with APIClient(base, timeout=3, max_retries=0) as client:
    client.session.trust_env = False
    wrapped = client.get_json("/health")
assert direct == wrapped == {"status": "ok"}
print("requests与APIClient业务结果一致")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.client_compare
```

**对照运行后的结果：** 手动服务正常时脚本退出0，打印两种结果一致。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两种方式看到同样的 health 业务结果。
- [ ] 能指出请求传输由 requests 完成，APIClient 负责哪些公共约束。
- [ ] 知道 `get_json` 默认期望 200，真实 API 不一定所有操作都返回 200。

**卡住时：** 连接错误先确认手动服务；脚本 import 失败时使用 `-m exercises.client_compare` 从根目录运行。

<a id="day-2"></a>

## 第 2 天：离线验证 query 与 JSON body

**材料：** `tests/api/test_responses_mock.py` 的 query、POST body 示例。

**操作：**

1. 在 `tests/test_client_extended.py` 导入 json、pytest、responses、`APIClient`；定义 `BASE = 'https://client.test'`。
2. 自写 GET `/search` 的 Mock：注册 200 JSON，用 client 传 `params={'q': 'hello world', 'page': 2}`，再断言调用次数、方法和 query。使用 `urllib.parse.urlparse/parse_qs` 比较解析结果，避免依赖 query 顺序或空格编码方式。
3. 自写 POST `/tasks` 的 Mock：注册 201 JSON；用 `post_json` 传标题，断言 `json.loads(responses.calls[0].request.body)` 等于输入字典，Content-Type 为 JSON。
4. 两条测试都用 `with APIClient(BASE, max_retries=0)` 关闭 session；每条加 `@responses.activate`。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

responses.activate保证这些地址由Mock接管。解析query、解析JSON后比较数据，不依赖URL参数顺序或JSON空格。返回的id=7只是Mock数据，不代表真实服务保存过任务。

文件 `tests/test_client_extended.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day02/tests/test_client_extended.py)

```python
import json
from urllib.parse import urlparse, parse_qs
import pytest
import requests
import responses
from core.api_client import APIClient, APIError

BASE = "https://client.test"


@responses.activate
def test_query_is_sent():
    responses.get(f"{BASE}/search", json={"items": []}, status=200)
    with APIClient(BASE, timeout=3, max_retries=0) as client:
        assert client.get_json("/search", params={"q": "hello world", "page": 2}) == {"items": []}
    assert len(responses.calls) == 1
    sent = responses.calls[0].request
    assert sent.method == "GET"
    assert parse_qs(urlparse(sent.url).query) == {"q": ["hello world"], "page": ["2"]}


@responses.activate
def test_json_body_is_sent():
    responses.post(f"{BASE}/tasks", json={"id": 7}, status=201)
    body = {"title": "client-test"}
    with APIClient(BASE, max_retries=0) as client:
        assert client.post_json("/tasks", body) == {"id": 7}
    assert len(responses.calls) == 1
    sent = responses.calls[0].request
    assert sent.method == "POST"
    assert sent.headers["Content-Type"] == "application/json"
    assert json.loads(sent.body) == body
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_client_extended.py -q
```

**对照运行后的结果：** 2 passed；不会向client.test发送真实请求。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两条自写离线测试通过；有发出请求的断言，不能只断言伪造响应。
- [ ] 合上样例能再补一个 query 参数并正确断言。
- [ ] 能说明这些测试证明请求构造，不证明真实服务有 `/search`。

**卡住时：** parse_qs 返回的值是列表，page 解析后为 `['2']`；HTTP 参数与 Python 数字的类型不同。

<a id="day-3"></a>

## 第 3 天：错误状态、空响应、非法 JSON 与 patch 边界

**材料：** `tests/test_client_contract.py::test_empty_response_and_invalid_json_are_distinct`，`tests/test_api_client.py` 的 patch 示例。

**操作：**

1. 增加显式期望 404 的测试：调用原始 `request`，断言拿到 Response，不把合法的异常场景当测试失败。
2. 增加 DELETE 204 的测试，只检查原始响应和空 body；不调用 JSON 方法。
3. 增加 GET 200、正文 `not-json` 的测试，用 `pytest.raises(requests.exceptions.JSONDecodeError)` 验证解析失败。
4. 在入门 patch 示例里找到被替换的名字，写出“在使用方查找该名字的位置 patch”的解释。邮件模拟为练习 02 选做；不连接真实 SMTP。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_api_client.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

前3条区分HTTP状态、无正文和JSON解析；第4条直接替换被当前客户端使用的session.request，演示patch的位置。_content只在构造测试Response时使用，不是日常访问响应的接口。

文件 `tests/test_client_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/05/day03/tests/test_client_extended.py)

```python
@responses.activate
def test_expected_404_returns_response():
    responses.get(f"{BASE}/tasks/404", json={"error": "not_found"}, status=404)
    with APIClient(BASE, max_retries=0) as client:
        response = client.request("GET", "/tasks/404", expect_status=404)
        assert response.status_code == 404
        assert response.json() == {"error": "not_found"}


@responses.activate
def test_delete_204_has_no_json():
    responses.delete(f"{BASE}/tasks/1", status=204)
    with APIClient(BASE, max_retries=0) as client:
        response = client.delete("/tasks/1", expect_status=204)
        assert response.content == b""


@responses.activate
def test_invalid_json_is_parse_error():
    responses.get(f"{BASE}/broken", body="not-json", status=200)
    with APIClient(BASE, max_retries=0) as client:
        with pytest.raises(requests.exceptions.JSONDecodeError):
            client.get_json("/broken")


def test_patch_at_used_session():
    from unittest.mock import patch
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"items": []}'
    with APIClient(BASE, timeout=3, max_retries=0) as client:
        with patch.object(client.session, "request", return_value=response) as mocked:
            assert client.get_json("/tasks") == {"items": []}
            mocked.assert_called_once_with("GET", f"{BASE}/tasks", timeout=3)
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_client_extended.py -q
```

**对照运行后的结果：** 累计6 passed，包含完整patch示例。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 自写 404、204、非法 JSON 三类场景通过。
- [ ] 能区别 APIError 的状态失败与 JSONDecodeError 的解析失败。
- [ ] 能解释 patch 与 responses 都无法证明远端真实行为。

**卡住时：** 200 不保证 JSON 合法；204 没有正文，不能用 `{}` 作为预期 JSON。

<a id="day-4"></a>

## 第 4 天：证明 GET 重试而 POST 不重放

**材料：** `APIClient.__init__` 中 Retry、`test_get_retries_transient_status`、`test_write_is_not_replayed`。

**操作：**

1. 自写 `test_get_retry_extended`：依次注册 GET 503、200，客户端 max_retries=1，最终成功且 `len(responses.calls) == 2`。
2. 自写关闭重试的对应测试：只注册 503，max_retries=0，显式期望 503，调用一次。
3. 自写 POST 503 测试：max_retries=2 也只调用一次，显式期望 503。
4. 在记录中画两种过程：HTTP 请求重试与 pytest 重跑整条用例。指出后者可能重新登录、创建数据、执行清理。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py -k 'retry or replay' -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

必须断言调用次数，才能证明“是否重放”。最终JSON正确不能独自证明首次请求没失败。POST即使配置了重试次数也不会自动重放。

文件 `tests/test_client_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/05/day04/tests/test_client_extended.py)

```python
@responses.activate
def test_get_retry_extended():
    responses.get(f"{BASE}/tasks", status=503)
    responses.get(f"{BASE}/tasks", json={"items": []}, status=200)
    with APIClient(BASE, max_retries=1) as client:
        assert client.get_json("/tasks") == {"items": []}
    assert len(responses.calls) == 2


@responses.activate
def test_get_no_retry_extended():
    responses.get(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=0) as client:
        assert client.request("GET", "/tasks", expect_status=503).status_code == 503
    assert len(responses.calls) == 1


@responses.activate
def test_post_is_not_replayed():
    responses.post(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=2) as client:
        response = client.request("POST", "/tasks", json={"title": "x"}, expect_status=503)
        assert response.status_code == 503
    assert len(responses.calls) == 1
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_client_extended.py -k 'retry or replay' -q
```

**对照运行后的结果：** 本日3 passed；GET调用次数2/1，POST为1。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] GET 两种配置的调用次数分别为 2、1，POST 为 1。
- [ ] 能说明最终 200 可能掩盖首次 503，故障排查应先关闭重试。
- [ ] 不把 POST 加到重试允许方法中；没有幂等约定时可能重复写入。

**卡住时：** 函数名包含 retry/replay 才会被此命令选中；检查 selected 数量，不把全 deselected 当通过。

<a id="day-5"></a>

## 第 5 天：验证日志与异常文本不包含凭据

**材料：** `test_logs_and_status_error_exclude_payloads`、[排障指南](../DEBUGGING.md) 的日志约束。

**操作：**

1. 自写一个 `caplog` 测试，使用 `secret-body-test`、`secret-header-test` 等假值分别放 body、Authorization、query、Mock 响应正文。
2. 在 `caplog.at_level(logging.INFO, logger='api')` 下故意触发状态码不符，捕获 APIError。
3. 合并 `caplog.text + str(caught.value)`，逐个断言假凭据不出现，同时断言方法或错误状态出现，证明日志并非完全没记录。
4. 检查自己前几天的学习记录是否误贴真实 token，移除值并保留字段名/状态码等必要证据。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py -k log -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

caplog记录api日志，caught保存异常对象。正向检查POST/400能证明并非“没有任何日志所以没有泄漏”；负向检查四种假凭据。真实凭据不用于此实验。

文件 `tests/test_client_extended.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/05/day05/tests/test_client_extended.py)

```python
@responses.activate
def test_logs_exclude_secrets(caplog):
    import logging
    responses.post(f"{BASE}/login", json={"token": "secret-response-test"}, status=400)
    with APIClient(BASE, max_retries=0) as client:
        client.set_token("secret-header-test")
        with caplog.at_level(logging.INFO, logger="api"):
            with pytest.raises(APIError) as caught:
                client.post_json("/login", {"password": "secret-body-test"},
                                 params={"key": "secret-query-test"})
    text = caplog.text + str(caught.value)
    assert "POST" in text
    assert "400" in text
    for secret in ["secret-response-test", "secret-header-test", "secret-body-test", "secret-query-test"]:
        assert secret not in text
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_client_extended.py -k log -q
```

**对照运行后的结果：** 本日1 passed；整个客户端扩展文件累计10条。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 四类假凭据均未泄漏，有正向日志存在断言。
- [ ] 能解释客户端日志安全不能自动保证自己写的 assert、print、CI 附件也安全。
- [ ] 能说出最小排障证据：方法、状态、异常类型、测试名、必要的脱敏字段。

**卡住时：** 使用假值；不要为了测试泄漏拿真实密码做实验。

<a id="day-6"></a>

## 第 6 天：完成三种故障实验并分别归因

**材料：** [排障指南](../DEBUGGING.md)，自己的 Mock 与 workflow 测试。

**操作：** 每种实验都记录触发条件、命令、失败节点、预期/实际、判断理由、恢复结果。

1. **非法响应：** Mock GET 200 的正文为非法 JSON，在一条临时诊断测试中直接调用 `get_json`，看到解析失败；正常回归版本用 raises 断言此异常。
2. **错误状态：** Mock GET 503，关闭重试且仍期望 200，看到 APIError 的状态不符；正常回归版本显式断言该异常。
3. **业务规则：** 临时把靶场标题上限由 80 改为 81，跑自己的长度 81 场景，应在期望 400 处失败。只恢复这一处后再跑通过。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py -v --tb=short
.\.venv\Scripts\python.exe -m pytest tests/workflow/test_tasks_extended.py -v --tb=short
```

临时诊断失败测试另存到 `exercises/diagnose_client.py`，需要时显式传路径运行；不要把永久故意失败文件留在默认 tests 收集目录。测试函数仍用 test_ 前缀。

```powershell
.\.venv\Scripts\python.exe -m pytest exercises/diagnose_client.py -v --tb=short
```

这条诊断命令预期失败；把它与捕获预期异常后应通过的正式客户端回归区分开。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

诊断文件放exercises，显式运行时应有2条失败；正式客户端测试仍应通过。第三个实验用真实本机HTTP验证81字符应被拒绝，故障脚本自动恢复源码。它是教学注入，不能写成线上缺陷。

文件 `exercises/diagnose_client.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day06/exercises/diagnose_client.py)

```python
import responses
from core.api_client import APIClient

BASE = "https://client.test"


@responses.activate
def test_diagnose_invalid_json():
    responses.get(f"{BASE}/broken", body="not-json", status=200)
    with APIClient(BASE, max_retries=0) as client:
        client.get_json("/broken")  # 故意不捕获：观察JSONDecodeError。


@responses.activate
def test_diagnose_bad_status():
    responses.get(f"{BASE}/tasks", status=503)
    with APIClient(BASE, max_retries=0) as client:
        client.get_json("/tasks")  # 默认期望200，故意观察APIError。
```

文件 `tests/workflow/test_title81_reference.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day06/tests/workflow/test_title81_reference.py)

```python
def test_title81_is_rejected(alice_client):
    before = alice_client.get_json("/tasks")
    assert alice_client.post_json("/tasks", {"title": "x" * 81}, expect_status=400) == {"error": "invalid_fields"}
    assert alice_client.get_json("/tasks") == before
```

文件 `exercises/verify_title_mutation.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day06/exercises/verify_title_mutation.py)

```python
from pathlib import Path
import subprocess
import sys

target = Path("sandbox/task_api.py")
original = target.read_bytes()
source = original.decode("utf-8")
old = "len(title.strip()) <= 80"
assert source.count(old) == 1
args = [sys.executable, "-B", "-m", "pytest", "tests/workflow/test_title81_reference.py", "-q"]
subprocess.run(args, check=True)
try:
    target.write_text(source.replace(old, "len(title.strip()) <= 81", 1), encoding="utf-8")
    assert subprocess.run(args).returncode == 1
finally:
    target.write_bytes(original)
subprocess.run(args, check=True)
print("81字符错误放行已被发现，服务源码已恢复")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
# 故意失败实验，预期退出码 1；核对下面的结果说明。
.\.venv\Scripts\python.exe -B -m pytest exercises/diagnose_client.py -q
.\.venv\Scripts\python.exe -B -m exercises.verify_title_mutation
```

**对照运行后的结果：** 诊断2 failed分别是解析/HTTP状态；业务规则注入时失败，恢复后通过，故障脚本最终0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 三次故障的证据不同，能分别归为解析、HTTP 状态、服务端业务规则。
- [ ] 业务规则实验不是语法错误，恢复后客户端与业务测试都通过。
- [ ] 不用加重试、跳过或修改预期来消除未知失败。

**卡住时：** Mock 故障验证诊断流程，不写成“发现线上服务缺陷”；主动注入的缺陷需明确标注。

<a id="day-7"></a>

## 第 7 天：写缺陷报告并完成客户端回归

**操作：**

1. 按排障模板写 `docs/bug_report_01.md`，选昨天业务规则实验：需求、最短复现命令、预期/实际、影响、根因、清理、恢复回归；标明主动注入。
2. 对照练习 02 第一部分六项要求，把自己新增测试名对应上；样例已覆盖但你未独立完成的项标清楚。
3. 跑客户端和完整默认回归，记录退出码：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_client_extended.py tests/test_client_contract.py tests/api/test_responses_mock.py
.\.venv\Scripts\python.exe -m pytest
$LASTEXITCODE
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

缺陷报告给出完整叙述，但本人实际执行信息必须据实补充。交付脚本只跑应通过的正式测试；诊断文件留在exercises，不把故意失败掺进默认tests。

文件 `docs/bug_report_01.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day07/docs/bug_report_01.md)

```markdown
# [标题校验] 81字符被错误接受（主动注入实验）

- 需求：去除首尾空白后title长度1—80，超出返回400且不创建。
- 前置：Alice登录，记录创建前列表。
- 最短复现：python -m exercises.verify_title_mutation。
- 注入：valid_title的上限从80改为81，仅此一处。
- 步骤：POST title='x'*81，预期400，再查列表不变。
- 预期：400 invalid_fields；无新任务。
- 注入后实际行为：201并生成任务；测试在客户端期望400处失败。
- 原因：合法性上限错误，未拒绝边界外输入。
- 影响：违反标题长度契约，可能使后续结构校验失败。
- 清理：实验使用pytest临时库；源码finally恢复；不触碰手动服务库。
- 修复验证：恢复80后原失败测试通过，并运行正常/边界/异常与默认回归。
- 本人执行日期、Python版本、实际测试输出和证据路径：执行后追加。
```

文件 `exercises/check_client_delivery.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/05/day07/exercises/check_client_delivery.py)

```python
import subprocess
import sys

subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_client_extended.py",
    "tests/test_client_contract.py", "tests/api/test_responses_mock.py", "-q"], check=True)
print("客户端扩展与基线回归通过；诊断故意失败文件未纳入默认收集")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.check_client_delivery
```

**对照运行后的结果：** 10条自写客户端测试与原有契约/Mock测试全部通过。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 请求构造、404/204/非法 JSON、重试、日志六项要求都有自写断言或明确证据。
- [ ] 三次故障与一份完整缺陷报告齐全，默认回归无临时故意失败测试。
- [ ] 合上源码，说明 Mock 的能力边界与请求重试的副作用。

**未通过怎么办：** 只会伪造返回值回第 2 天；异常混淆回第 3/6 天；根因写不清先补复现证据。
