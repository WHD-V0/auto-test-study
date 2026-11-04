# 练习 02：隔离依赖与验证客户端行为

目标：知道哪些行为适合 Mock，哪些必须通过真实服务验证。材料：`tests/test_api_client.py`、`tests/api/test_responses_mock.py`、`tests/test_client_contract.py`。

## 第一部分：HTTP 客户端

用 responses 给 `core.api_client.APIClient` 增加以下测试，不访问网络：

1. 查询参数和 JSON body 被正确构造；通过解析 JSON 比较数据，不依赖序列化空格或字段顺序。
2. 显式期望 404 能返回原始 Response，204 不尝试调用 json。
3. 返回非法 JSON 时，明确是解析失败而不是业务成功。
4. 关闭重试时，503 原样进入状态码断言；开启重试时 GET 的 503→200 最多调用两次。
5. POST 返回 503 不自动重放；说明为什么添加 POST 到 allowed_methods 可能重复写入。
6. 日志和 APIError 文本不包含密码、token、query 或响应正文。

## 第二部分：邮件依赖（可选）

自行实现 `src/notification.py` 的 EmailSender，通过 SMTP 上下文管理器执行 starttls/login/sendmail。仅捕获预期的 SMTP/OSError 类异常并返回 False，编程错误应暴露。

在 `tests/test_notification.py` 用 `patch('src.notification.smtplib.SMTP')` 模拟；通过 `mock_smtp.return_value.__enter__.return_value` 验证 login/sendmail，模拟连接异常。禁止连接真实邮件服务器，使用假凭据。

验收：成功和异常分支都有请求/调用断言；能解释 patch 应打在使用方的名字上；能说清 Mock 通过仍不能证明远端鉴权、数据库或邮件投递正确。
