def test_cleanup_probe(task_factory):
    task_factory("cleanup-probe")
    assert False, "故意失败，用于观察teardown；实验结束删掉本文件"
