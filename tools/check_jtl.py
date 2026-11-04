"""检查 JMeter CSV JTL，断言失败或样本缺失时返回非零状态。"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def summarize(path: Path, expected_samples: int | None = None) -> dict:
    required = {"timeStamp", "elapsed", "label", "responseCode", "success"}
    groups = {}
    total = failures = 0
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("JTL 缺少必需的 CSV 列")
        for row in reader:
            try:
                elapsed = int(row["elapsed"])
                timestamp = int(row["timeStamp"])
                success = row["success"].strip().lower()
                if elapsed < 0 or timestamp < 0 or success not in {"true", "false"} or not row["label"]:
                    raise ValueError("invalid sample")
            except (ValueError, TypeError, AttributeError) as exc:
                raise ValueError(f"JTL 第 {reader.line_num} 行不是有效样本") from exc
            group = groups.setdefault(row["label"], {"elapsed": [], "failures": 0})
            group["elapsed"].append(elapsed)
            group["failures"] += success == "false"
            total += 1
            failures += success == "false"
    if total == 0:
        raise ValueError("JTL 没有样本")
    if expected_samples is not None and total != expected_samples:
        raise ValueError(f"样本数不符: expected={expected_samples}, actual={total}")
    labels = {}
    for label, group in sorted(groups.items()):
        values = sorted(group["elapsed"])
        labels[label] = {"samples": len(values), "failures": group["failures"],
                         "p95_ms_nearest_rank": values[math.ceil(len(values) * 0.95) - 1]}
    return {"samples": total, "failures": failures, "labels": labels}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-samples", type=int)
    args = parser.parse_args()
    if args.expected_samples is not None and args.expected_samples <= 0:
        parser.error("expected-samples 必须大于 0")
    try:
        result = summarize(args.path, args.expected_samples)
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, f"JTL check failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if result["failures"] else 0)


if __name__ == "__main__":
    main()
