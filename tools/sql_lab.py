"""创建专用 SQL 训练库，或用只读连接执行命名查询。"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def initialize(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # 只创建新的文件，拒绝覆盖已有数据库。
    path.touch(exist_ok=False)
    with closing(sqlite3.connect(path)) as db:
        db.executescript((SQL_DIR / "seed.sql").read_text(encoding="utf-8"))


def query(path: Path, name: str) -> list[dict]:
    query_path = SQL_DIR / "queries" / f"{name}.sql"
    if query_path not in list((SQL_DIR / "queries").glob("*.sql")):
        raise ValueError("未知命名查询")
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        return [dict(row) for row in db.execute(query_path.read_text(encoding="utf-8"))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="创建新训练库，不覆盖文件")
    init.add_argument("--db", type=Path, required=True)
    select = commands.add_parser("query", help="只读命名查询")
    select.add_argument("--db", type=Path, required=True)
    select.add_argument("--name", choices=sorted(p.stem for p in (SQL_DIR / "queries").glob("*.sql")), required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.db)
            print(f"Created training database: {args.db}")
        else:
            print(json.dumps(query(args.db, args.name), ensure_ascii=False, indent=2))
    except (OSError, sqlite3.Error, ValueError) as exc:
        parser.exit(1, f"SQL lab failed: {exc}\n")


if __name__ == "__main__":
    main()
