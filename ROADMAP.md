# 接口自动化测试 · 4 周速成路线

> 目标：不是"会写几个测试"，而是达到**可以直接上项目**的工作水准。
> 每周结束都有一个里程碑，做到了再往下走。

## 你现在有什么

- `src/` + `tests/`：pytest 单元测试基础（断言 / fixture / mock / 参数化）
- `core/` + `config/` + `data/`：企业级接口测试框架骨架
- `tests/api/`：真实接口测试、responses 离线测试、数据驱动三套范例

**学习方式：先读懂范例 → 改造它 → 做 exercises → 换一个公共接口从头写。**

---

## 第 1 周：pytest 基础打牢（单元测试部分）

**每天 1-2 小时。材料：`tests/test_calculator.py`、`test_user_service.py`、`test_parametrize.py`、`exercises/exercise_01_basic.md`**

- [ ] Day 1-2：函数级测试。断言、`pytest.raises`、测试命名规范。手写 10 个测试
- [ ] Day 3-4：fixture。`yield` 前后置、fixture 互相调用、`scope` 作用域、`tmp_path` / `capsys` 内置 fixture
- [ ] Day 5：参数化。`parametrize`、`ids`、`pytest.param` 标记个别数据
- [ ] Day 6-7：运行与调试。`-k` 筛选、`--tb=short`、`-x` 首败即停、`pytest.ini` 配置

**里程碑**：能独立完成 `exercise_01_basic.md`，说清楚"fixture 和普通函数传参有什么区别"。

## 第 2 周：接口测试核心技能

**材料：`tests/api/test_responses_mock.py`、`core/api_client.py`、`exercises/exercise_02_mock.md`**

- [ ] Day 1-2：HTTP 基础 + requests。方法、状态码、headers、query/body。读 `core/api_client.py` 直到每行都懂
- [ ] Day 3-4：responses 离线测试。逐个跑 `test_responses_mock.py`，理解每个用例为什么这么写
- [ ] Day 5：异常分支。超时、5xx、状态码不符——接口测试一半价值在这里
- [ ] Day 6-7：mock 进阶。`patch`、`MagicMock`、`side_effect`，完成 `exercise_02_mock.md`

**里程碑**：给你一个没见过的封装类，能不碰网络就测完它所有分支。

## 第 3 周：企业级接口自动化实战

**材料：`tests/api/test_jsonplaceholder_real.py`、`test_data_driven.py`、`config/`、`data/`**

- [ ] Day 1-2：跑通真实接口用例，理解"状态码 + Schema + 业务字段"三层断言
- [ ] Day 3：JSON Schema。给 `/comments`、`/albums` 等新接口各写一个 Schema
- [ ] Day 4：CRUD 链路 + 接口依赖。仿写 `test_full_crud`，处理 token 传递（`set_token` 的用法）
- [ ] Day 5：数据驱动。往 `data/users.yaml` 加数据，观察用例自动增加；换 `reqres.in` 重写一遍
- [ ] Day 6-7：**大作业** —— 完成 `exercise_03_api.md`：为公共接口从零搭一套用例

**里程碑**：不参照本项目，能独立为任意 REST 接口写出结构合理的测试。

## 第 4 周：工程化与面试能力（拉开差距的部分）

- [ ] Day 1：框架分层思想。能画出本项目 `config / core / data / tests` 的分层图，说清每层职责
- [ ] Day 2：报告与并行。`pytest --html=reports/report.html --self-contained-html`、`pytest -n auto`、`--reruns 2`
- [ ] Day 3：CI。写一个 GitHub Actions，push 自动跑测试并上传报告（可让 AI 帮你生成）
- [ ] Day 4-5：**大作业** —— 完成 `exercise_04_framework.md`：设计一个你自己的接口测试框架
- [ ] Day 6：简历 + 面试题准备（见下）
- [ ] Day 7：复盘，把本项目所有 exericse 重做一遍

**里程碑**：有自己的框架作品 + 一个能跑的 CI，简历上可以写"独立搭建接口自动化测试框架"。

---

## 企业面试高频考点（速成时按此自查）

1. pytest fixture 的 scope 有哪几种？conftest.py 的加载机制？
2. 接口测试怎么设计用例？（正常 / 边界 / 异常 / 鉴权 / 幂等 / 并发）
3. mock 和 responses/stub 的区别？什么场景必须 mock？
4. 接口之间有依赖怎么处理？（token 传递、数据上下文、setup 用例）
5. 测试数据怎么管理？（配置分离、数据驱动、敏感信息环境变量）
6. 用例失败了怎么定位？（分层断言、日志、报告、重试机制的利弊）
7. 你的框架怎么设计的？为什么这么分层？（第 4 周大作业就是答案）

## 常用命令速查

```bash
pytest                                   # 全量运行
pytest -m "not real_api"                 # 离线跑（跳过真实接口）
pytest -m smoke                          # 只跑冒烟
pytest tests/api -v --tb=short           # 指定目录 + 简短报错
pytest --html=reports/report.html --self-contained-html   # HTML 报告
pytest -n auto                           # 多进程并行
pytest --reruns 2                        # 失败自动重试 2 次
TEST_ENV=dev pytest                      # 切换环境
```
