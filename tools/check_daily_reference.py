"""在临时项目副本检查逐日参考代码，不修改学习者的 src/tests 文件。

运行：python -m tools.check_daily_reference [--static-only] [--stage 1]
语法/链接检查不替代真实 Linux、远程 CI 或 JMeter 引擎实测。
"""
from __future__ import annotations

import argparse
import ast
import csv
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "docs" / "daily" / "reference"
BASE_TESTS = [
    "__init__.py", "test_calculator.py", "test_user_service.py", "test_parametrize.py",
    "test_api_client.py", "test_client_contract.py", "test_jtl_check.py",
    "api/__init__.py", "api/test_responses_mock.py", "workflow/conftest.py",
    "workflow/test_tasks.py", "workflow/test_database_checks.py",
]


def run(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=180)


def checked_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"路径越界: {relative}")
    return path


def static_checks(lessons):
    assert {(item["stage"], item["day"]) for item in lessons} == {
        (stage, day) for stage in range(1, 10) for day in range(1, 8)
    }
    counts = {"python": 0, "powershell": 0, "bash": 0, "jmx": 0, "yaml": 0, "links": 0}
    for item in lessons:
        assert item["artifacts"], (item["stage"], item["day"])
        for artifact in item["artifacts"]:
            if artifact["mode"] == "delete":
                continue
            path = checked_path(REFERENCE, artifact["source"])
            source = path.read_text(encoding="utf-8-sig")
            if path.suffix == ".py":
                ast.parse(source, filename=str(path))
                counts["python"] += 1
            elif path.suffix == ".yml":
                data = yaml.safe_load(source)
                assert "jobs" in data
                counts["yaml"] += 1
            elif path.suffix == ".jmx":
                tree = ET.fromstring(source)
                assert len(tree.findall(".//HTTPSamplerProxy")) == (9 if item["stage"] == 9 else 7)
                for node in tree.iter("hashTree"):
                    children = list(node)
                    assert len(children) % 2 == 0
                    assert all(children[index].tag == "hashTree" for index in range(1, len(children), 2))
                counts["jmx"] += 1
    for chapter in (ROOT / "docs/daily").glob("[0-9][0-9]-*.md"):
        text = chapter.read_text(encoding="utf-8")
        assert text.count("<!-- daily-reference:start -->") == 7
        assert text.count("**当天写完后的参考代码：**") == 7
        # 文档中的Python代码也需可解析，避免嵌入时截断或转义出错。
        for code in re.findall(r"^```python\n(.*?)^```", text, re.M | re.S):
            ast.parse(code, filename=str(chapter))
        stage = int(chapter.name[:2])
        sections = re.split(r'(?=<a id="day-[1-7]"></a>)', text)
        for item in (item for item in lessons if item["stage"] == stage):
            for artifact in item["artifacts"]:
                if artifact["mode"] != "delete":
                    source = checked_path(REFERENCE, artifact["source"]).read_text(encoding="utf-8-sig")
                    assert source.rstrip() in sections[item["day"]], (chapter, artifact["source"])
    documents = [ROOT / "README.md", ROOT / "ROADMAP.md", *(ROOT / "docs/daily").glob("*.md"),
                 REFERENCE / "README.md", *(ROOT / "exercises").glob("*.md")]
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for href in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
            if "://" in href:
                continue
            relative, _, fragment = unquote(href).partition("#")
            target = (document.parent / relative).resolve() if relative else document
            assert target.exists(), (document, href)
            if fragment:
                content = target.read_text(encoding="utf-8-sig")
                anchors = set(re.findall(r'<a id="([^"]+)"', content))
                for heading in re.findall(r'^#{1,6} (.+)$', content, re.M):
                    slug = ''.join(c for c in heading.lower() if c.isalnum() or c in '_- ')
                    anchors.add(slug.replace(' ', '-'))
                assert fragment in anchors, (document, href)
            counts["links"] += 1
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell:
        command = r"""
$lessonFiles = Get-ChildItem -LiteralPath $args[0] -Recurse -Filter '*.ps1'
foreach ($lessonFile in $lessonFiles) {
    $lessonTokens = $null
    $lessonErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($lessonFile.FullName, [ref]$lessonTokens, [ref]$lessonErrors)
    if ($lessonErrors.Count -gt 0) { throw ($lessonFile.FullName + ': ' + ($lessonErrors.Message -join '; ')) }
}
Write-Output $lessonFiles.Count
"""
        # -File avoids PowerShell -Command argument re-parsing of paths.
        with tempfile.TemporaryDirectory(dir=ROOT / "reports/learning") as directory:
            parser_file = Path(directory) / "parse.ps1"
            parser_file.write_text(command, encoding="utf-8-sig")
            result = run([powershell, "-NoProfile", "-File", str(parser_file), str(REFERENCE)], ROOT)
            assert result.returncode == 0, result.stderr + result.stdout
            counts["powershell"] = int(result.stdout.strip())
    git = shutil.which("git")
    bash_candidates = [Path(git).resolve().parents[1] / "bin/bash.exe"] if git else []
    if os.name != "nt" and shutil.which("bash"):
        bash_candidates.append(Path(shutil.which("bash")))
    bash = next((path for path in bash_candidates if path.is_file()), None)
    if bash:
        for file in REFERENCE.rglob("*.sh"):
            result = run([str(bash), "-n", file.as_posix()], ROOT)
            assert result.returncode == 0, result.stderr
            counts["bash"] += 1
    print("STATIC PASS:", json.dumps(counts, ensure_ascii=False), flush=True)
    return counts


def copy_baseline(workspace):
    for folder in ("src", "core", "config", "sandbox", "sql", "tools", "data"):
        for source in (ROOT / folder).rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                continue
            target = workspace / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    for filename in ("conftest.py", "pytest.ini", "requirements.txt"):
        shutil.copyfile(ROOT / filename, workspace / filename)
    for filename in BASE_TESTS:
        target = workspace / "tests" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "tests" / filename, target)
    (workspace / "exercises").mkdir(exist_ok=True)
    (workspace / "exercises/__init__.py").touch()


def apply_artifact(workspace, artifact):
    target = checked_path(workspace, artifact["target"])
    if artifact["mode"] == "delete":
        target.unlink(missing_ok=True)
        return
    text = checked_path(REFERENCE, artifact["source"]).read_text(encoding="utf-8-sig")
    target.parent.mkdir(parents=True, exist_ok=True)
    if artifact["mode"] == "append":
        text = (target.read_text(encoding="utf-8").rstrip() + "\n\n" if target.exists() else "") + text
    elif artifact["mode"] == "replace_function":
        original = target.read_text(encoding="utf-8")
        node = next(node for node in ast.parse(original).body
                    if isinstance(node, ast.FunctionDef) and node.name == artifact["name"])
        start = min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)]) - 1
        lines = original.splitlines(keepends=True)
        text = "".join(lines[:start]) + text + "".join(lines[node.end_lineno:])
    target.write_text(text, encoding="utf-8-sig" if target.suffix == ".ps1" else "utf-8", newline="\n")


@contextmanager
def local_service(workspace, env):
    code = ("from pathlib import Path; from sandbox.task_api import create_server; "
            "s=create_server(Path('reports/reference-service.sqlite3')); "
            "print('http://127.0.0.1:'+str(s.server_port),flush=True); s.serve_forever()")
    process = subprocess.Popen([sys.executable, "-B", "-u", "-c", code], cwd=workspace, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, encoding="utf-8", errors="replace")
    try:
        url = process.stdout.readline().strip()
        if not url.startswith("http://127.0.0.1:"):
            raise RuntimeError("临时服务启动失败: " + process.stderr.read())
        yield {**env, "LESSON_BASE_URL": url}
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()


def check_lesson(item, workspace, env):
    for spec in item["checks"]:
        result = run([sys.executable, "-B", *spec["args"]], workspace, env)
        output = result.stdout + result.stderr
        assert result.returncode == spec["exit_code"], (
            f"{item['stage']}-{item['day']}: {spec['args']}\n{output[-8000:]}"
        )
        assert all(text in output for text in spec["contains"]), output[-8000:]
        if item["stage"] == 3 and item["day"] == 4:
            assert "ERROR at teardown" not in output, output[-8000:]


def check_metric_script(workspace, env):
    """构造CSV仅测试统计脚本，不把它报告成JMeter压测结果。"""
    for threads in (1, 2, 5):
        path = workspace / f"reports/learning/jmeter/t{threads}day05/results.jtl"
        path.parent.mkdir(parents=True, exist_ok=True)
        labels = ["01_login"] * threads
        labels += [label for _ in range(threads * 10) for label in
                   ("02_create", "03_read", "04_update", "05_verify_update", "06_delete", "07_verify_deleted")]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["timeStamp", "elapsed", "label", "responseCode", "success"])
            writer.writeheader()
            for index, label in enumerate(labels):
                writer.writerow(dict(timeStamp=1000 + index * 100, elapsed=10,
                                     label=label, responseCode=200, success="true"))
    result = run([sys.executable, "-B", "-m", "exercises.jmeter.report_metrics"], workspace, env)
    assert result.returncode == 0, result.stdout + result.stderr
    content = (workspace / "performance/my_metrics.md").read_text(encoding="utf-8")
    rows = [line for line in content.splitlines() if line.startswith("| ")]
    assert len(rows) == 22  # 1表头 + 7个label×3档；分隔行以|---开头。
    assert "| 1 | 02_create | 10 | 0 | 0% | 10 |" in content
    assert "| 5 | 01_login | 5 | 0 | 0% | 10 |" in content
    print("METRICS PASS: synthetic CSV fixture only; no JMeter load executed", flush=True)


def runtime_checks(lessons, stages):
    completed = 0
    service_days = {(2, 1), (2, 2), (2, 3), (5, 1), (9, 7)}
    with tempfile.TemporaryDirectory(prefix="reference-check-", dir=ROOT / "reports/learning") as directory:
        temporary_root = Path(directory).resolve()
        assert temporary_root.is_relative_to((ROOT / "reports/learning").resolve())
        for stage in stages:
            workspace = temporary_root / f"stage{stage:02}"
            workspace.mkdir()
            copy_baseline(workspace)
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8",
                   "PYTHONPATH": str(workspace)}
            for item in [item for item in lessons if item["stage"] == stage]:
                for artifact in item["artifacts"]:
                    apply_artifact(workspace, artifact)
                if stage == 8 and item["day"] == 6:
                    check_metric_script(workspace, env)
                if not item["checks"]:
                    continue
                if (stage, item["day"]) in service_days:
                    with local_service(workspace, env) as service_env:
                        check_lesson(item, workspace, service_env)
                else:
                    check_lesson(item, workspace, env)
                completed += 1
                print(f"RUNTIME PASS: {stage}-{item['day']} ({len(item['checks'])} commands)", flush=True)
    print(f"RUNTIME PASS: {completed} learning days; learner files unchanged", flush=True)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--stage", type=int, choices=range(1, 10))
    args = parser.parse_args()
    (ROOT / "reports/learning").mkdir(parents=True, exist_ok=True)
    lessons = json.loads((REFERENCE / "manifest.json").read_text(encoding="utf-8"))["lessons"]
    static_checks(lessons)
    if not args.static_only:
        runtime_checks(lessons, [args.stage] if args.stage else range(1, 10))


if __name__ == "__main__":
    main()
