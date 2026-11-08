import argparse
import csv
import math
from pathlib import Path
from collections import defaultdict
from tools.check_jtl import summarize

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path("reports/learning/jmeter"))
parser.add_argument("--output", type=Path, default=Path("performance/my_metrics.md"))
args = parser.parse_args()
if args.output.exists():
    parser.error("输出已存在，请用--output指定新文件，避免覆盖个人报告")
lines = ["# 本轮真实JTL指标", "", "P95采用nearest-rank；吞吐单位samples/s，按每个label自身首样本开始至末样本结束的窗口计算。", "",
    "| 线程 | label | 样本 | 失败 | 错误率 | P95 ms | 吞吐 samples/s |",
    "|---|---|---|---|---|---|---|"]
for threads in (1, 2, 5):
    path = args.root / f"t{threads}day05/results.jtl"
    summary = summarize(path, threads * 61)
    assert summary["failures"] == 0, f"{path}有失败，先分析原因"
    groups = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            groups[row["label"]].append(row)
    for label, rows in sorted(groups.items()):
        elapsed = sorted(int(row["elapsed"]) for row in rows)
        p95 = elapsed[math.ceil(len(elapsed) * 0.95) - 1]
        first = min(int(row["timeStamp"]) for row in rows)
        last = max(int(row["timeStamp"]) + int(row["elapsed"]) for row in rows)
        seconds = (last - first) / 1000
        throughput = f"{len(rows) / seconds:.2f}" if seconds > 0 else "窗口为0，不能计算"
        lines.append(f"| {threads} | {label} | {len(rows)} | 0 | 0% | {p95} | {throughput} |")
lines += ["", "数据来自各档独立JTL。不同于Dashboard口径时先对照时间窗和算法，不篡改原始数据。", "",
          "此表仅为本机实验指标，不证明线上容量；环境、资源观测和原因分析另见my_report.md。"]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("已生成：", args.output)
