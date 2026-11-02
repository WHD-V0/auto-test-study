# 练习 03：真实接口测试实战

> 目标：脱离本项目现成代码，独立为一个新接口写出企业水准的测试。
> 靶场：https://reqres.in（免费公共接口测试站，支持登录 / 注册 / 用户 CRUD）
> 预计用时：一个下午

## 背景知识

reqres.in 常用接口：

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/users?page=2` | GET | 分页用户列表 |
| `/api/users/{id}` | GET | 单个用户（id=23 返回 404，可测异常） |
| `/api/users` | POST | 创建用户，返回 201 |
| `/api/users/{id}` | PUT | 更新用户 |
| `/api/users/{id}` | DELETE | 删除用户，返回 204 |
| `/api/register` | POST | 注册（`password` 缺失返回 400） |
| `/api/login` | POST | 登录，返回 token |

## 任务清单（按顺序做，全部手动从零写）

### 第一部分：环境与分层（30 分）
1. 在 `config/config.yaml` 里新增 `reqres` 环境配置
2. 写一个 conftest fixture `reqres_client`，返回指向 reqres 的 `APIClient`
3. 思考题：为什么用独立 fixture 而不是改掉现有的 `api_client`？

### 第二部分：查询接口（30 分）
4. GET 用户列表：断言状态码、分页字段（page/per_page/total）、data 是数组且每个元素符合 Schema
5. GET 单用户：Schema 校验 + `data.email` 以 `@reqres.in` 结尾
6. GET 不存在用户：`expect_status=404` 的异常用例

### 第三部分：写入接口与鉴权（40 分）
7. POST 创建用户：断言 201、返回体包含提交的字段
8. PUT 更新：创建 -> 更新 -> 断言字段变化
9. DELETE：断言 204（提示：204 时响应体为空，`get_json` 会炸，想想怎么处理）
10. 登录接口：成功返回 `token`；**把 token 设置到 client 上，验证后续请求头**
11. 登录异常：缺 password 返回 400 + `error` 字段

### 第四部分：数据驱动（加分）
12. 用 `data/` 目录新建 yaml，参数化测试至少 3 个注册/登录场景（成功 + 2 种失败）

## 验收标准（对照自查）

- [ ] 没有任何 URL 硬编码在测试里
- [ ] 每个接口至少 1 正常 + 1 异常用例
- [ ] 响应体断言用了 Schema，不是逐字段手写
- [ ] `pytest tests/api/test_reqres*.py` 全绿
- [ ] 能回答：为什么 204 要特殊处理？token 传递放在 fixture 还是测试里？

## 提示

- 卡住了先看 `tests/api/` 下的三个范例文件，找"最像的那一个"改
- `resp.request` 可以拿到原始 requests.Response 对象自己断言
- 做完可以让我帮你 review
