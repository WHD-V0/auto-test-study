# 练习 01：先明确边界，再编写测试

每天怎么做：[阶段一逐日教程](../docs/daily/01-python-pytest.md)。这是一周逐步完成的作业，不要求第一天写完；当天是否完成按教程中的勾选与证据判断。

目标：掌握断言、参数化、异常和 fixture；区分“实现刚好这样”和“需求要求这样”。

在 `src/string_utils.py` 实现以下函数，测试放在 `tests/test_string_utils.py`。

| 函数 | 约定 |
|---|---|
| reverse_string(s) | 反转字符串，空串返回空串 |
| is_palindrome(s) | 忽略大小写和普通空格，判断回文；空串视为回文 |
| count_vowels(s) | 统计英文字母 a/e/i/o/u，不区分大小写 |
| truncate(s, max_len, suffix='...') | 返回总长度不超过 max_len 的字符串；无需截断时原样返回 |

共同约定：s 必须为 str，否则 TypeError。truncate 的 max_len 必须为非 bool 的整数，否则 TypeError；小于 0 为 ValueError；suffix 必须为 str。参数合法性先于“无需截断”判断。需要截断且 max_len 小于 suffix 长度时，只返回 suffix 的前 max_len 个字符；等于时返回完整 suffix；否则正文占 max_len-len(suffix) 个字符。

示例：`truncate('hello world', 8)` 得到 `hello...`；max_len=2 得到 `..`；max_len=0 得到空串；`truncate('hello', 10)` 返回 hello。边界有明确约定后再写测试。

任务：每个函数至少 3 个测试，truncate 覆盖 max_len=0、后缀长度前后边界、非法类型与负数；至少一组参数化带 ids；用 tmp_path/yield 写一次文件准备和清理演示。

验收：测试单独运行与全量运行都通过；故意把“<=”改成“<”或移除参数校验，至少一个测试能捕获对应缺陷。提交说明测试发现了什么，而不仅是通过数量。
