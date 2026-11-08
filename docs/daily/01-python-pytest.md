# 阶段一：从第一条断言到独立测试

[返回每日目录](README.md) · [下一阶段](02-http-design.md) · 作业依据：[练习 01](../../exercises/exercise_01_basic.md)

本阶段先用计算器理解测试，再逐步完成字符串工具。命令都在项目根目录的 PowerShell 执行；环境准备见 [手册首页](README.md#开始前准备一次)。已有 `tests/test_day01.py` 时在其中补充，不覆盖自己的内容。

<a id="day-1"></a>

## 第 1 天：写出并运行第一个测试（45—60 分钟）

**今天的目标：** 会把“输入 → 实际结果 → 与预期比较”写成测试，并看懂一次失败。

**打开材料：** `src/calculator.py` 的 `Calculator.add`。先不看其他类、fixture 和参数化。

**跟着操作：**

1. 先在纸上写：2+3 应为 5，-2+(-3) 应为 -5，5+0 应为 5。预期来自加法规则。
2. 打开或新建 `tests/test_day01.py`，输入下面这条测试：

```python
from src.calculator import Calculator


def test_add():
    calc = Calculator()
    actual = calc.add(2, 3)
    assert actual == 5
```

`import` 引入计算器；`def test_add()` 定义测试；`Calculator()` 创建对象；`actual` 保存实际返回值；`assert` 要求条件成立，不成立就失败。文件和函数的 `test_` 前缀让 pytest 找到它。

3. 在终端运行：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_day01.py -v
```

4. 只把 `assert actual == 5` 改为 `assert actual == 6`，重跑。找到失败行和 `assert 5 == 6`。这是预期写错，不是计算器坏了。恢复成 5，再跑。
5. 先尝试写 `test_add_negative_numbers`、`test_add_zero`，再对照下方完整代码补全，分别覆盖纸上的另外两组数据，每个函数都自己创建计算器。运行同一命令。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

三个函数各自创建计算器，互不依赖。actual 是实际结果，右边的常量是运行前确定的预期。把第一个预期暂时改成 6，应该只让第一条失败；恢复为 5 后三条通过。

文件 `tests/test_day01.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day01/tests/test_day01.py)

```python
from src.calculator import Calculator


def test_add():
    calc = Calculator()
    actual = calc.add(2, 3)
    assert actual == 5


def test_add_negative_numbers():
    calc = Calculator()
    assert calc.add(-2, -3) == -5


def test_add_zero():
    calc = Calculator()
    assert calc.add(5, 0) == 5
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_day01.py -q
```

**对照运行后的结果：** 当天这份文件为 3 passed；故意改错第一条后为 1 failed、2 passed，恢复后 3 passed。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 自写的三条加法测试通过；文件若还有其他测试，实际总数可以更多。
- [ ] 保存故意写错预期时的失败行，恢复后通过。
- [ ] 合上教程，说出 `actual` 和 `5` 分别代表什么，以及为什么测试名要以 `test_` 开头。

**卡住时：** `==` 是比较，`=` 是赋值；检查函数内四个空格缩进。没有收集到测试时回到文件名、函数名检查。今天不要求完成练习 01。

<a id="day-2"></a>

## 第 2 天：浮点数、异常与第一组字符串测试

**打开材料：** `src/calculator.py` 的 `divide`，`tests/test_calculator.py` 中 `test_floats`、`test_divide_by_zero`；练习 01 的 `reverse_string` 约定。

**跟着操作：**

1. 在 `tests/test_day01.py` 引入 `pytest`，加一条测试：`assert Calculator().add(0.1, 0.2) == pytest.approx(0.3)`。临时换成直接 `== 0.3`，观察失败并恢复。`approx` 用于允许合理误差，不用于字符串或状态码。
2. 加一条除零测试，用 `with pytest.raises(ValueError, match="除数不能为零"):` 包住 `Calculator().divide(10, 0)`。这里“按约定抛异常”才是通过。
3. 新建 `tests/test_string_utils.py`，从 `src.string_utils` 导入 `reverse_string`，先写普通字符串、空串、非字符串三个场景。非字符串应抛 `TypeError`。
4. 新建 `src/string_utils.py`，实现类型检查与反转，让测试通过。最初模块不存在造成的导入错误只表示尚未实现，不能当成测试捕获了逻辑缺陷。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_day01.py tests/test_string_utils.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

s[::-1] 对列表也能反转，所以列表场景能证明类型校验确实存在。raises 内执行被测操作；函数按约定抛异常时，测试本身通过。approx 只解决浮点数的合理误差。

文件 `tests/test_day01.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/01/day02/tests/test_day01.py)

```python
import pytest


def test_add_floats():
    assert Calculator().add(0.1, 0.2) == pytest.approx(0.3)


def test_divide_by_zero():
    with pytest.raises(ValueError, match="除数不能为零"):
        Calculator().divide(10, 0)
```

文件 `src/string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day02/src/string_utils.py)

```python
def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return s[::-1]
```

文件 `tests/test_string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day02/tests/test_string_utils.py)

```python
import pytest
from src.string_utils import reverse_string


def test_reverse_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_empty():
    assert reverse_string("") == ""


def test_reverse_rejects_list():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_day01.py tests/test_string_utils.py -q
```

**对照运行后的结果：** 计算器累计 5 条、字符串 3 条，共 8 passed。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 浮点比较和除零测试都通过；能说明为什么抛异常的用例也是 `PASSED`。
- [ ] `reverse_string` 至少三个场景通过；把实现临时改为直接返回输入，普通字符串测试会失败，恢复后通过。
- [ ] 学习记录中各写一例：“测试预期写错”和“实现写错”如何区分。

**卡住时：** `pytest.raises` 内只放预期抛异常的操作，后续断言不要错误缩进进去；类型标注不会自动检查参数类型。

<a id="day-3"></a>

## 第 3 天：fixture 的依赖与每条测试的数据隔离

**打开材料：** `tests/test_user_service.py` 的 `service`、`service_with_users` 和 `TestAddUser`；`src/user_service.py`。

**跟着操作：**

1. 画出 `test_add_duplicate_raises → service_with_users → service` 的依赖关系，标明谁创建空服务、谁加两个用户。
2. 新建 `tests/test_day03_fixtures.py`，自己写一个默认 function 作用域的 `service` fixture，返回 `UserService()`。
3. 写两个测试：第一个添加自己的假用户并验证可查到；第二个拿到 `service` 时断言用户列表为空。不要让第二个依赖第一个的执行顺序。
4. 在本文件 fixture 内加准备打印，运行下面命令，观察每个测试都会准备一次。再临时改为 `scope="session"`，观察共享对象导致的污染；恢复 function。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_day03_fixtures.py -v -s --setup-show
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

默认 function 作用域会为两条测试分别调用 service。临时改为 @pytest.fixture(scope="session") 后，按本文件顺序执行时第二条会看到第一条留下的用户；恢复默认后重新通过。

文件 `tests/test_day03_fixtures.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day03/tests/test_day03_fixtures.py)

```python
import pytest
from src.user_service import User, UserService


@pytest.fixture
def service():
    print("prepare service")
    return UserService()


def test_add_user(service):
    user = User("Learner", "learner@example.com", 20)
    service.add_user(user)
    assert service.get_user("learner@example.com") is user


def test_service_starts_empty(service):
    assert service.list_users() == []
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_day03_fixtures.py -q -s
```

**对照运行后的结果：** 2 passed，并有两次 prepare service；session 实验会出现共享状态造成的失败。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 两条测试分别单独运行、合起来运行都通过。
- [ ] 能解释：fixture 名作为函数参数时由 pytest 注入，不需要自己调用 `service()`。
- [ ] 记录 function 与 session 的准备次数；恢复后服务状态不跨测试共享。

**卡住时：** 不要在模块顶层创建一个共享 `UserService` 再让 fixture 返回它。清理打印等调试代码后保留实验结论。

<a id="day-4"></a>

## 第 4 天：用 yield 与 tmp_path 真正清理文件

**打开材料：** `tests/test_user_service.py::TestPersistence::test_save_and_load`，根目录 `conftest.py` 的 `temp_file`。它只是返回路径；今天要自己补一次明确的清理演示。

**跟着操作：** 在 `tests/test_day03_fixtures.py` 增加以下 fixture，再自己写测试读取内容为 `hello`：

```python
@pytest.fixture
def prepared_file(tmp_path):
    path = tmp_path / "lesson.txt"
    path.write_text("hello", encoding="utf-8")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
        assert not path.exists()
        print("cleaned:", path)
```

1. 第一次正常读取并通过，观察测试结束后 `cleaned` 输出。
2. 临时把测试内内容预期改成 `wrong`，观察测试失败时依然有清理输出，且 teardown 的不存在断言通过。
3. 恢复正确预期。再自己写保存用户到 `tmp_path / 'users.json'` 后用新 `UserService` 加载的测试，断言姓名和邮箱。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_day03_fixtures.py -v -s --setup-show
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

这段追加到昨天的文件，沿用 pytest、User、UserService 和 service。finally 即使遇到测试断言失败也执行。保存和加载使用不同对象，避免只检查原对象而漏掉文件持久化。

文件 `tests/test_day03_fixtures.py` — 追加到该文件末尾；若已有同名函数则对照更新，只保留一份。 [打开参考文件](reference/01/day04/tests/test_day03_fixtures.py)

```python
@pytest.fixture
def prepared_file(tmp_path):
    path = tmp_path / "lesson.txt"
    path.write_text("hello", encoding="utf-8")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)
        assert not path.exists()
        print("cleaned:", path)


def test_read_prepared_file(prepared_file):
    assert prepared_file.read_text(encoding="utf-8") == "hello"


def test_save_and_load(service, tmp_path):
    service.add_user(User("Learner", "learner@example.com", 20))
    path = tmp_path / "users.json"
    service.save_to_file(str(path))
    restored = UserService()
    restored.load_from_file(str(path))
    user = restored.get_user("learner@example.com")
    assert user is not None
    assert user.name == "Learner"
    assert user.email == "learner@example.com"
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_day03_fixtures.py -q -s
```

**对照运行后的结果：** 文件累计 4 passed，出现 cleaned；把读取预期临时改为 wrong 时该条失败但仍打印 cleaned。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 正常和故意断言失败时都验证了文件被删除；记录准备、测试、清理的顺序。
- [ ] 保存/加载使用不同服务对象，能验证真实文件往返。
- [ ] 能解释 `yield` 前是准备、后是清理；`tmp_path` 由 pytest 提供，不手写固定临时目录。

**卡住时：** 清理断言失败显示为 teardown `ERROR`，要排查，不能当作业务通过；失败实验完成后恢复测试。

<a id="day-5"></a>

## 第 5 天：参数化，并补回文和元音统计

**打开材料：** `tests/test_parametrize.py` 的第一组参数化，练习 01 中 `is_palindrome`、`count_vowels` 规则。

**跟着操作：**

1. 在 `tests/test_string_utils.py` 写 `is_palindrome` 的参数化：`'Never odd or even' → True`、`'hello' → False`、`'' → True`；加 `ids=['spaces-case', 'not-palindrome', 'empty']`。这里只忽略普通空格和大小写，不擅自去掉所有标点。
2. 写 `count_vowels` 的参数化：`'AEiou' → 5`、`'rhythm' → 0`、`'' → 0`。
3. 两个函数各加非字符串输入抛 `TypeError` 的测试，再到 `src/string_utils.py` 实现它们。
4. 临时写错一个参数的 expected，观察失败名中的 id；用完整 nodeid 单独重跑，随后恢复。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_string_utils.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_string_utils.py --collect-only -q
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

提供的是本日结束后的完整字符串模块与测试文件；与自己的代码对比合并，不重复定义同名函数。lower 处理大小写，replace 只移除普通空格。元音计数把每个 True 计为 1。

文件 `src/string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day05/src/string_utils.py)

```python
def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return s[::-1]



def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    normalized = s.lower().replace(" ", "")
    return normalized == normalized[::-1]


def count_vowels(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return sum(char in "aeiou" for char in s.lower())
```

文件 `tests/test_string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day05/tests/test_string_utils.py)

```python
import pytest
from src.string_utils import reverse_string


def test_reverse_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_empty():
    assert reverse_string("") == ""


def test_reverse_rejects_list():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])

from src.string_utils import is_palindrome, count_vowels


@pytest.mark.parametrize("text,expected", [
    ("Never odd or even", True), ("hello", False), ("", True), ("Abba", True),
], ids=["spaces-case", "not-palindrome", "empty", "mixed-case"])
def test_palindrome(text, expected):
    assert is_palindrome(text) is expected


@pytest.mark.parametrize("text,expected", [("AEiou", 5), ("rhythm", 0), ("", 0)],
                         ids=["all-vowels", "no-vowels", "empty"])
def test_count_vowels(text, expected):
    assert count_vowels(text) == expected


@pytest.mark.parametrize("function", [is_palindrome, count_vowels],
                         ids=["palindrome", "vowels"])
def test_text_functions_reject_non_string(function):
    with pytest.raises(TypeError):
        function(123)
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_string_utils.py -q
```

**对照运行后的结果：** 字符串文件共 12 passed；用 -k mixed-case 可以只选中 Abba 那组。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 每个函数至少三种业务输入，还覆盖类型错误。
- [ ] 能从失败的 id 找到数据行，并解释参数名字如何对应测试函数参数。
- [ ] 无需参考样例，新增 `'Abba' → True` 后通过。

**卡住时：** ids 数量必须对应参数行数；`--collect-only` 只收集不执行，不能把收集成功当成测试通过。

<a id="day-6"></a>

## 第 6 天：从边界表实现 truncate，并缩小失败范围

**打开材料：** 练习 01 的完整 `truncate` 约定，先不写实现。

**跟着操作：**

1. 在学习记录中列出下表预期；为每行写测试，再实现 `truncate`。

| 输入（默认 suffix='...'） | 预期 |
|---|---|
| `'hello world', 8` | `'hello...'` |
| `'hello world', 0 / 2 / 3 / 4` | `'' / '..' / '...' / 'h...'` |
| `'hello', 5 / 10` | 均为 `'hello'` |
| `max_len=-1` | `ValueError` |
| `max_len=True / 2.5 / '8'` | 均为 `TypeError` |
| 非字符串 s / 非字符串 suffix | `TypeError` |

2. 再加 `truncate('hi', 10, suffix=None)` 应抛 `TypeError`，验证参数检查先于无需截断判断；添加一个自定义后缀场景。
3. 临时把一个预期写错，用下面命令观察 `-x` 只在第一处失败后停止、`--tb=short` 缩短堆栈，再恢复。

**运行：**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_string_utils.py -k truncate -x --tb=short
.\.venv\Scripts\python.exe -m pytest tests/test_string_utils.py -v
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

这是四个函数和全部测试的完整版本。len(s)<=max_len 要先于拼后缀；需要截断时正文与后缀一起受总长度限制。先排除 bool，再检查 int，因为 isinstance(True,int) 为 True。

文件 `src/string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day06/src/string_utils.py)

```python
def reverse_string(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return s[::-1]



def is_palindrome(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    normalized = s.lower().replace(" ", "")
    return normalized == normalized[::-1]


def count_vowels(s):
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    return sum(char in "aeiou" for char in s.lower())



def truncate(s, max_len, suffix="..."):
    # 所有参数先校验，不能因字符串短就跳过非法参数。
    if not isinstance(s, str):
        raise TypeError("s 必须是字符串")
    if isinstance(max_len, bool) or not isinstance(max_len, int):
        raise TypeError("max_len 必须是非 bool 的整数")
    if max_len < 0:
        raise ValueError("max_len 不能为负数")
    if not isinstance(suffix, str):
        raise TypeError("suffix 必须是字符串")
    if len(s) <= max_len:
        return s
    if max_len <= len(suffix):
        return suffix[:max_len]
    return s[:max_len - len(suffix)] + suffix
```

文件 `tests/test_string_utils.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day06/tests/test_string_utils.py)

```python
import pytest
from src.string_utils import reverse_string


def test_reverse_normal():
    assert reverse_string("hello") == "olleh"


def test_reverse_empty():
    assert reverse_string("") == ""


def test_reverse_rejects_list():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])

from src.string_utils import is_palindrome, count_vowels


@pytest.mark.parametrize("text,expected", [
    ("Never odd or even", True), ("hello", False), ("", True), ("Abba", True),
], ids=["spaces-case", "not-palindrome", "empty", "mixed-case"])
def test_palindrome(text, expected):
    assert is_palindrome(text) is expected


@pytest.mark.parametrize("text,expected", [("AEiou", 5), ("rhythm", 0), ("", 0)],
                         ids=["all-vowels", "no-vowels", "empty"])
def test_count_vowels(text, expected):
    assert count_vowels(text) == expected


@pytest.mark.parametrize("function", [is_palindrome, count_vowels],
                         ids=["palindrome", "vowels"])
def test_text_functions_reject_non_string(function):
    with pytest.raises(TypeError):
        function(123)

from src.string_utils import truncate


@pytest.mark.parametrize("text,limit,expected", [
    ("hello world", 8, "hello..."), ("hello world", 0, ""),
    ("hello world", 2, ".."), ("hello world", 3, "..."),
    ("hello world", 4, "h..."), ("hello", 5, "hello"), ("hello", 10, "hello"),
], ids=["normal", "zero", "below-suffix", "equal-suffix", "above-suffix", "exact", "no-cut"])
def test_truncate_boundaries(text, limit, expected):
    result = truncate(text, limit)
    assert result == expected
    assert len(result) <= limit


@pytest.mark.parametrize("limit", [True, 2.5, "8"], ids=["bool", "float", "string"])
def test_truncate_invalid_limit_type(limit):
    with pytest.raises(TypeError):
        truncate("hello", limit)


def test_truncate_negative_limit():
    with pytest.raises(ValueError):
        truncate("hello", -1)


def test_truncate_invalid_text():
    with pytest.raises(TypeError):
        truncate(123, 8)


def test_truncate_validates_suffix_before_no_cut():
    with pytest.raises(TypeError):
        truncate("hi", 10, suffix=None)


def test_truncate_custom_suffix():
    assert truncate("abcdef", 4, suffix="~") == "abc~"
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/test_string_utils.py -q
```

**对照运行后的结果：** 字符串文件共 26 passed；-k truncate 选中 14 条。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 表内场景、自定义后缀、无需截断但参数非法的场景都通过。
- [ ] 能说明 `bool` 在 Python 中与 `int` 的关系，以及为何要显式排除它。
- [ ] 记录一个失败的输入、预期、实际和代码行，不只写“红了”。

**卡住时：** 先区分“是否需要截断”，再计算总长度；suffix 长度也算在上限内。时间不足就分两次完成当天。

<a id="day-7"></a>

## 第 7 天：闭卷复写与证明测试有效

**打开材料：** 练习 01 的验收要求，只看需求，不看现有测试答案。

**跟着操作：**

1. 新建 `tests/test_week01_review.py`，独立重写正常、空串边界、非法类型三个字符串场景，至少有一个异常断言。
2. 临时移除 `reverse_string` 的类型校验，用 `['a', 'b']` 测试应捕获未抛 `TypeError` 的缺陷。恢复；再临时移除 `truncate` 对负数的校验，确认负数场景失败并恢复。只改自己本周实现的局部。
3. 运行独立复习文件、字符串作业，最后跑默认回归：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_week01_review.py -v
.\.venv\Scripts\python.exe -m pytest tests/test_string_utils.py -v
.\.venv\Scripts\python.exe -m pytest
```




<!-- daily-reference:start -->
**当天写完后的参考代码：**

先自己做闭卷题，再对照四条参考测试。故障脚本每次从原始源码生成一种缺陷，并在 finally 恢复；它不会提交缺陷。Python 使用 -B 避免快速改回时复用旧字节码。

文件 `tests/test_week01_review.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day07/tests/test_week01_review.py)

```python
import pytest
from src.string_utils import reverse_string, is_palindrome, truncate


def test_review_normal():
    assert reverse_string("python") == "nohtyp"


def test_review_empty():
    assert is_palindrome("") is True


def test_review_invalid_type():
    with pytest.raises(TypeError):
        reverse_string(["a", "b"])


def test_review_suffix_boundary():
    assert truncate("abcdef", 3) == "..."
```

文件 `exercises/verify_string_mutations.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/01/day07/exercises/verify_string_mutations.py)

从项目根目录以 python -m exercises.verify_string_mutations 运行；try/finally 保证实验后恢复原始文件字节。

```python
from pathlib import Path
import subprocess
import sys

target = Path("src/string_utils.py")
original = target.read_bytes()
source = original.decode("utf-8")
experiments = [
    ("if not isinstance(s, str):", "if False:", "reverse_rejects_list"),
    ("if max_len < 0:", "if False:", "truncate_negative_limit"),
]
try:
    for old, new, selector in experiments:
        assert old in source, f"找不到待修改代码: {old}"
        target.write_text(source.replace(old, new, 1), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", "-m", "pytest",
            "tests/test_string_utils.py", "-k", selector, "-q", "-p", "no:cacheprovider"])
        assert result.returncode == 1, "应因目标断言失败，而非收集或环境错误"
        target.write_bytes(original)
finally:
    target.write_bytes(original)
subprocess.run([sys.executable, "-B", "-m", "pytest", "tests/test_string_utils.py",
                "tests/test_week01_review.py", "-q"], check=True)
print("两种缺陷均被捕获，源码已恢复")
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -B -m exercises.verify_string_mutations
```

**对照运行后的结果：** 两次子测试各 1 failed 属于预期；恢复后 30 passed，脚本最终退出 0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 练习 01 的四个函数各至少三个测试，truncate 完整边界、带 ids 的参数化、yield 文件清理均有证据。
- [ ] 自写测试单独与全量运行通过；两次缺陷注入各在目标断言失败，恢复后通过。
- [ ] 不看教程能写一个测试，解释一处需求边界和一次失败原因。

**未通过怎么办：** 不会断言回第 1—2 天；数据污染回第 3—4 天；边界遗漏回第 6 天。完成后整理 `docs/learning_log.md`，再进入阶段二。
