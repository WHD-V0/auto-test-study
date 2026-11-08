# 归档用例（参考设计）

| 编号 | 前置/操作 | 预期 |
|---|---|---|
| A01 | done→archived | 200；GET同ID为archived |
| A02 | open→archived | 409；原值不变 |
| A03 | archived→open | 409；原值不变 |
| A04 | archived→done | 409；原值不变 |
| A05 | archived修改title | 409；完整对象不变 |
| A06 | archived查询 | 200；ID/owner/状态正确 |
| A07 | archived删除后再查 | 204空体→404 |
| A08 | 默认列表 | 含本次open/done，不含archived |
| A09 | include_archived=false | 同默认 |
| A10 | include_archived=true | 本次三状态都存在，仅当前用户 |
| A11 | 参数为other或空字符串 | 400 |
| A12 | Bob读/改/删Alice归档 | 均403；Alice再查未变 |
| A13 | open提交合法新title+archived | 409；title/status均不变 |
| A14 | SQL核对归档成功 | 同ID/owner的status为archived |
| A15 | SQL核对被拒转换 | before/open均不变 |

所有资源由工厂登记，归档可DELETE清理；HTTP与SQL断言分别证明公开行为和落库。
