# 我的任务用例表（参考成品；执行状态需本人填写）

| 编号 | 需求/风险 | 前置/输入 | 预期状态与业务/副作用 | 清理 | 优先级 | 对应测试 |
|---|---|---|---|---|---|---|
| C01 | 最小合法长度 | Alice；title='x' | 201；再查 title=x、owner=alice、status=open | 工厂按 ID 删 | P1 | test_title_boundaries[min] |
| C02 | 最大合法长度 | Alice；80 字符 | 201；再查长度80 | 工厂按 ID 删 | P1 | test_title_boundaries[max] |
| C03 | 超长 | Alice；81 字符 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[too-long] |
| C04 | 全空白 | Alice；三个空格 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_title_invalid[blank] |
| C05 | 错误类型 | Alice；title=123 | 400 invalid_fields；列表不变 | 不应创建 | P1 | test_invalid_title_number |
| C06 | 首尾空白 | Alice；title='  hello  ' | 201；再查为hello | 工厂按 ID 删 | P1 | test_title_boundaries[trim] |
