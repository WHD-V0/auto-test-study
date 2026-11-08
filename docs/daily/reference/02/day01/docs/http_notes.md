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
