# 接口自动化测试学习项目

> 学习路线见 **[ROADMAP.md](ROADMAP.md)** —— 4 周速成到工作水准的完整计划

## 项目结构

```
auto-test-study/
├── README.md              # 项目说明
├── ROADMAP.md             # 4 周速成学习路线（先看这个）
├── requirements.txt       # 依赖清单
├── pytest.ini             # pytest 配置（含 markers）
├── conftest.py            # pytest 全局 fixture（api_client、test_data 等）
├── config/                # 【框架层】多环境配置
│   ├── config.yaml        #   环境定义（test/dev），URL 与超时集中管理
│   └── settings.py        #   配置加载器（支持 TEST_ENV 环境变量切换）
├── core/                  # 【框架层】核心封装
│   ├── api_client.py      #   企业级 API 客户端：统一入口/重试/鉴权/日志
│   └── validator.py       #   JSON Schema 响应结构校验
├── data/                  # 【框架层】测试数据（数据驱动）
│   └── users.yaml
├── src/                   # 【教学层】被测源代码（单元测试练手用）
├── src/                   # 被测源代码
│   ├── __init__.py
│   ├── calculator.py      # 计算器模块（基础示例）
│   ├── user_service.py    # 用户服务模块（中级示例）
│   └── api_client.py      # API 客户端模块（进阶示例）
├── tests/                 # 测试用例
│   ├── api/               # 接口自动化测试（重点）
│   │   ├── test_jsonplaceholder_real.py  # 真实接口：CRUD/Schema/异常（@real_api）
│   │   ├── test_responses_mock.py        # responses 离线接口测试
│   │   └── test_data_driven.py           # yaml 数据驱动
│   ├── test_calculator.py # 基础测试示例
│   ├── test_user_service.py # 中级测试示例
│   ├── test_api_client.py # 进阶测试示例（含 mock）
│   └── test_parametrize.py # 参数化测试示例
└── exercises/             # 练习题
    ├── exercise_01_basic.md
    ├── exercise_02_mock.md
    ├── exercise_03_api.md      # 接口测试实战（reqres.in）
    └── exercise_04_framework.md # 毕业项目：设计自己的框架
```

## 快速开始

```bash
# 1. 进入项目目录
cd D:\pythonProject\auto-test-study

# 2. 安装依赖
pip install -r requirements.txt

# 3. 全量运行（含真实接口用例，需要网络）
pytest

# 4. 离线运行（跳过真实接口用例，日常推荐）
pytest -m "not real_api"

# 5. 生成 HTML 测试报告
pytest --html=reports/report.html --self-contained-html

# 6. 并行执行 / 失败重试
pytest -n auto
pytest --reruns 2
```

## 学习路线

1. **第 1 周 · 基础篇**：`tests/test_calculator.py` — 断言、基本测试结构
2. **第 1 周 · 中级篇**：`tests/test_user_service.py` — fixture、setUp/tearDown
3. **第 1 周 · 参数化**：`tests/test_parametrize.py` — 数据驱动测试
4. **第 2 周 · Mock**：`tests/test_api_client.py` + `tests/api/test_responses_mock.py`
5. **第 3 周 · 接口实战**：`tests/api/test_jsonplaceholder_real.py`、`test_data_driven.py`
6. **练习**：`exercises/` — 每周配套动手实践
7. **完整计划**：`ROADMAP.md` — 含里程碑、面试考点、常用命令

## 核心概念

### 1. 测试函数命名
```python
def test_功能描述():
    assert 实际结果 == 期望结果
```

### 2. Fixture（夹具）
```python
@pytest.fixture
def my_fixture():
    # 准备工作
    obj = Something()
    yield obj
    # 清理工作
```

### 3. 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (3, 4),
])
def test_example(input, expected):
    assert input + 1 == expected
```

### 4. Mock（模拟）
```python
from unittest.mock import patch, MagicMock

with patch.object(obj, "method") as mock:
    mock.return_value = "fake"
    result = obj.method()
    assert result == "fake"
```

## 常见问题

**Q: pytest 运行卡住怎么办？**  
A: 尝试 `python -m pytest tests/` 或检查是否有无限循环的代码。

**Q: 如何只运行某个测试？**  
A: `pytest tests/test_calculator.py::TestAdd::test_positive_numbers`

**Q: 如何查看 print 输出？**  
A: 加 `-s` 参数：`pytest -s`

**Q: 测试失败如何调试？**  
A: 加 `--tb=short` 查看简短错误栈，或 `--tb=long` 查看详细栈。
