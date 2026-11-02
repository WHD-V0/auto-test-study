"""响应校验器 —— 学习要点：用 JSON Schema 做"结构断言"

逐字段 assert 适合小响应；字段一多就会失控。
企业做法是定义 Schema（响应长什么样），一条语句校验整个结构：
  - 字段是否存在、类型对不对
  - 列表元素结构是否一致
  - 哪些字段可以忽略（值不关心）
"""
from __future__ import annotations

from typing import Any

from jsonschema import Draft7Validator, FormatChecker


def validate(data: Any, schema: dict) -> list[str]:
    """按 schema 校验数据，返回所有错误描述（空列表 = 通过）"""
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    return [f"字段 {'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in validator.iter_errors(data)]


def assert_schema(data: Any, schema: dict, context: str = "响应") -> None:
    """校验失败直接抛 AssertionError，消息里带上全部错误（pytest 报告友好）"""
    errors = validate(data, schema)
    if errors:
        raise AssertionError(f"{context}不符合 Schema:\n  - " + "\n  - ".join(errors))
