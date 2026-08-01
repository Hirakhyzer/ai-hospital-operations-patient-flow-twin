import json
import subprocess
import sys


def test_pipeline_smoke(tmp_path):
    output_dir = tmp_path / "outputs"
    result = subprocess.run(
        [sys.executable, "scripts/run_synthetic_hospital_lab.py", "--units", "5", "--arrivals", "90", "--hours", "24", "--seed", "11", "--output-dir", str(output_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(result.stdout)
    assert summary["synthetic_unit_count"] == 5
    assert summary["synthetic_arrival_count"] == 90
    assert (output_dir / "results" / "synthetic_hospital_flow_summary.json").exists()
    assert (output_dir / "reports" / "synthetic_hospital_operations_report.md").exists()
    assert (output_dir / "audit" / "hospital_operations_audit_log.jsonl").exists()
    assert (output_dir / "figures" / "synthetic_capacity_pressure.png").exists()
