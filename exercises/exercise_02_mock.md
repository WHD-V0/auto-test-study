# 练习 2：Mock 与外部依赖

## 目标
学习使用 mock 隔离外部依赖（数据库、文件系统、网络请求）。

## 待测代码

```python
# src/notification.py（你需要先创建这个文件）

import smtplib
from email.mime.text import MIMEText


class EmailSender:
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send(self, to: str, subject: str, body: str) -> bool:
        """发送邮件，成功返回 True，失败返回 False"""
        try:
            msg = MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = to

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, [to], msg.as_string())
            return True
        except Exception:
            return False
```

## 任务

1. 创建 `src/notification.py`
2. 创建 `tests/test_notification.py`
3. 使用 `unittest.mock.patch` 模拟 `smtplib.SMTP`，测试：
   - 发送成功时返回 `True`
   - SMTP 连接失败时返回 `False`
   - 验证 `server.login` 被正确调用
   - 验证 `server.sendmail` 的参数
4. **不要真的连接任何邮件服务器**

## 提示
- 用 `patch("src.notification.smtplib.SMTP")` 模拟 SMTP
- 用 `MagicMock` 的 `__enter__` / `__exit__` 模拟上下文管理器
- 用 `side_effect = Exception("连接失败")` 模拟异常

## 示例代码（使用 unittest.mock，无需安装额外包）

```python
from unittest.mock import patch, MagicMock

def test_example():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"key": "value"}

    with patch.object(obj, "method", return_value=mock_resp):
        result = obj.method()
        assert result == {"key": "value"}
```
