# [归档列表] 默认查询泄漏归档任务（主动注入）

需求：缺省include_archived时列表排除archived。
前置：Alice通过API准备open、done、archived各一条。
步骤：去掉默认过滤后GET /tasks。
预期：含本次open/done，不含archived。
注入后行为：SQL仍按owner隔离但未过滤状态，归档ID出现在默认列表。
证据测试：test_default_list_excludes_archived[default/false]。
根因：默认列表SQL遗漏status过滤，结构及HTTP200仍正确，需业务断言发现。
修复：恢复过滤；默认/false排除，true可查；权限、排序、SQL、并行回归。
实际日期、运行输出、JMX/JTL/检查器退出码与报告位置：本人执行后追加。
