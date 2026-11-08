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
