from hospitaltwin.audit import append_record, verify_log


def test_audit_log_verifies(tmp_path):
    path = tmp_path / "audit.jsonl"
    append_record(path, {"event": "start"})
    append_record(path, {"event": "finish"})
    result = verify_log(path)
    assert result["valid"] is True
    assert result["record_count"] == 2
