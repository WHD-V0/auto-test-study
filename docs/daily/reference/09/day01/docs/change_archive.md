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
