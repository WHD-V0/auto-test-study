# 失败定位与缺陷记录

## 先缩小复现范围

使用虚拟环境解释器执行：

```text
python -m pytest tests/workflow/test_tasks.py::test_full_crud -vv --tb=short
python -m pytest tests/workflow -x
python -m pytest --collect-only -q
```

先不加 `--reruns`。同一个场景单独运行、顺序运行、并行运行结果不同，优先检查共享 token、硬编码 ID、数据库隔离和未清理数据。公共 API 连接失败时先确认目标环境、代理、访问要求；不能跳过断言把红色变成绿色。

## 按失败证据定位

| 现象 | 先核对 | 下一步 |
|---|---|---|
| APIError 网络错误 | 服务是否启动、地址和超时 | 重现连接，检查服务日志与环境，不当作服务端业务缺陷 |
| 状态码不符 | 契约、认证上下文、输入 | 本地查看脱敏后的响应，记录 X-Request-ID |
| JSON 解析失败 | Content-Type、204 或 HTML 错误页 | 使用原始 Response 判断，不能假定所有成功响应都是 JSON |
| Schema 失败 | 字段缺失、类型变化 | 分清契约变更与服务实现错误 |
| 业务断言失败 | 输入值、owner、更新后再查询 | 核对持久化和权限，记录最小复现步骤 |
| teardown 失败 | 清理请求及资源 ID | 修复数据回收，保留清理失败，不覆盖原始失败 |

`resp` 是 `requests.Response`；`resp.request` 是 `PreparedRequest`，可检查实际请求方法、URL、headers 和 body。只有本地排查需要时查看，分享或写入报告之前必须脱敏。

客户端只记录方法、状态、耗时和异常类型，不记录请求体、query、token、完整 URL 或响应体。pytest 的断言文本、插件附加信息和 traceback 仍可能暴露你主动写入的敏感内容；真实项目需一起检查报告与 CI artifact。使用本地假凭据练习。

## 重试不能替代定位

- 请求层只对 GET/HEAD/OPTIONS 的指定 5xx 做有限重试；本项目关闭连接/读取异常自动重放，不重放 POST/PUT/DELETE。
- 自动重试会让部分瞬时故障在最终成功后不显现。验收测试或排查故障时用 `APIClient(max_retries=0)` 观察第一次响应。
- pytest 的 `--reruns` 会重跑整条测试，可能再次创建数据或执行其他副作用。CI 默认不启用；只有已识别的偶发环境问题才考虑临时使用，并记录负责人和移除条件。

## 缺陷报告模板

```text
标题：[任务更新] 非法 status 导致 title 被部分写入
版本 / 环境 / Python 版本：
需求依据：API_CONTRACT，更新原子性
最短复现命令 / 脱敏请求：
前置：Alice 创建 title=before、status=open 的任务
步骤：PUT 提交 title=after、status=unknown；GET 同一 ID
预期：PUT 400，GET 仍为 before/open
实际：填写实际状态码与字段，不能只写“断言失败”
证据：测试 nodeid、响应字段、X-Request-ID、报告位置
影响：非法更新破坏已有数据
清理：登记资源 ID，删除结果
修复后：原失败用例通过，相关正常/异常场景回归通过
```

故障实验：在本地故意去掉越权检查、让更新只返回新值却不写数据库、接受 81 字符标题，分别观察测试是否失败。每次只改一处，实验后恢复，禁止把缺陷注入提交到共享服务。
