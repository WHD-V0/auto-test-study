"""验证 JTL 门槛不会把 HTTP 200 的业务断言失败或缺失样本判为通过。"""
import pytest
from tools.check_jtl import summarize

HEADER = "timeStamp,elapsed,label,responseCode,success\n"


def test_failed_assertion_with_200_is_counted(tmp_path):
    path = tmp_path / "results.jtl"
    path.write_text(HEADER + "1000,10,read,200,true\n1010,20,read,200,false\n", encoding="utf-8")
    result = summarize(path, expected_samples=2)
    assert result["samples"] == 2
    assert result["failures"] == 1
    assert result["labels"]["read"]["p95_ms_nearest_rank"] == 20


def test_expected_404_can_be_successful(tmp_path):
    path = tmp_path / "results.jtl"
    path.write_text(HEADER + "1000,2,verify_deleted,404,true\n", encoding="utf-8")
    assert summarize(path, expected_samples=1)["failures"] == 0


def test_incomplete_run_is_rejected(tmp_path):
    path = tmp_path / "results.jtl"
    path.write_text(HEADER + "1000,2,login,200,true\n", encoding="utf-8")
    with pytest.raises(ValueError, match="actual=1"):
        summarize(path, expected_samples=19)


@pytest.mark.parametrize("content", [HEADER, "wrong,columns\n1,2\n", HEADER + "1000,NaN,read,200,true\n"])
def test_empty_or_malformed_jtl_is_rejected(tmp_path, content):
    path = tmp_path / "results.jtl"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        summarize(path)
