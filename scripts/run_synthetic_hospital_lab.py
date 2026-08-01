"""Run the independent synthetic hospital operations and patient-flow digital twin.

The command uses only fictional units, bed inventory, staff rosters, patient
arrivals, operating-room queues, and ambulance handoffs. It demonstrates
patient-flow forecasting, capacity auditing, staff workload analysis, delay
bottleneck review, synthetic equity audit, scenario comparison, reporting,
figures, and a hash-chained audit log.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hospitaltwin.audit import append_record, verify_log
from hospitaltwin.capacity import audit_capacity, capacity_summary
from hospitaltwin.config import ensure_output_dirs, set_seed
from hospitaltwin.delays import audit_delays, delay_summary
from hospitaltwin.equity import audit_equity, equity_summary
from hospitaltwin.flow import flow_summary, forecast_patient_flow
from hospitaltwin.reporting import write_report
from hospitaltwin.scenarios import compare_strategies, scenario_summary
from hospitaltwin.staffing import audit_staffing, staffing_summary
from hospitaltwin.synthetic import SyntheticHospitalConfig, generate_synthetic_hospital_data
from hospitaltwin.visualization import (
    plot_arrivals_by_hour,
    plot_capacity_pressure,
    plot_delay_bottlenecks,
    plot_equity_gap,
    plot_scenario_comparison,
    plot_staff_workload,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a synthetic hospital operations patient-flow digital twin.")
    parser.add_argument("--units", type=int, default=8)
    parser.add_argument("--arrivals", type=int, default=720)
    parser.add_argument("--hours", type=int, default=72)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    set_seed(args.seed)
    outputs = ensure_output_dirs(args.output_dir)
    data = generate_synthetic_hospital_data(SyntheticHospitalConfig(units=args.units, arrivals=args.arrivals, hours=args.hours, seed=args.seed))

    units = data["units"]
    beds = data["beds"]
    staff = data["staff"]
    arrivals = data["arrivals"]
    or_queue = data["or_queue"]
    handoffs = data["handoffs"]

    flow = forecast_patient_flow(arrivals, units, beds)
    capacity = audit_capacity(units, beds, flow, or_queue)
    staffing = audit_staffing(staff, flow)
    delay = audit_delays(arrivals, handoffs, or_queue, capacity)
    equity = audit_equity(arrivals)
    comparison = compare_strategies(flow, capacity, staffing, delay, equity)

    summary = {
        "seed": args.seed,
        "synthetic_unit_count": int(len(units)),
        "synthetic_arrival_count": int(len(arrivals)),
        "synthetic_staff_record_count": int(len(staff)),
        "synthetic_or_case_count": int(len(or_queue)),
        "synthetic_ambulance_handoff_count": int(len(handoffs)),
        "data_origin": "synthetic fictional hospital operations and patient-flow data",
        "decision_boundary": "hospital planning support only; not medical advice, triage, clinical decision support, or real-time patient safety software",
    }
    summary.update(flow_summary(flow))
    summary.update(capacity_summary(capacity))
    summary.update(staffing_summary(staffing))
    summary.update(delay_summary(delay))
    summary.update(equity_summary(equity))
    summary.update(scenario_summary(comparison))

    units.to_csv(outputs["results"] / "synthetic_hospital_units.csv", index=False)
    beds.to_csv(outputs["results"] / "synthetic_bed_inventory.csv", index=False)
    staff.to_csv(outputs["results"] / "synthetic_staff_roster.csv", index=False)
    arrivals.to_csv(outputs["results"] / "synthetic_patient_arrivals.csv", index=False)
    or_queue.to_csv(outputs["results"] / "synthetic_operating_room_queue.csv", index=False)
    handoffs.to_csv(outputs["results"] / "synthetic_ambulance_handoffs.csv", index=False)
    flow.to_csv(outputs["results"] / "synthetic_patient_flow_forecast.csv", index=False)
    capacity.to_csv(outputs["results"] / "synthetic_capacity_audit.csv", index=False)
    staffing.to_csv(outputs["results"] / "synthetic_staffing_audit.csv", index=False)
    delay.to_csv(outputs["results"] / "synthetic_delay_bottleneck_audit.csv", index=False)
    equity.to_csv(outputs["results"] / "synthetic_equity_waittime_audit.csv", index=False)
    comparison.to_csv(outputs["results"] / "synthetic_scenario_comparison.csv", index=False)

    audit_path = outputs["audit"] / "hospital_operations_audit_log.jsonl"
    append_record(audit_path, {**summary, "boundary": "independent synthetic hospital operations planning support only"})
    summary["audit_log"] = verify_log(audit_path)
    (outputs["results"] / "synthetic_hospital_flow_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    write_report(outputs["reports"] / "synthetic_hospital_operations_report.md", summary, flow, capacity, staffing, delay, equity, comparison)
    plot_arrivals_by_hour(arrivals, outputs["figures"] / "synthetic_arrivals_by_hour.png")
    plot_capacity_pressure(capacity, outputs["figures"] / "synthetic_capacity_pressure.png")
    plot_staff_workload(staffing, outputs["figures"] / "synthetic_staff_workload.png")
    plot_delay_bottlenecks(delay, outputs["figures"] / "synthetic_delay_bottlenecks.png")
    plot_equity_gap(equity, outputs["figures"] / "synthetic_equity_waittime_gap.png")
    plot_scenario_comparison(comparison, outputs["figures"] / "synthetic_scenario_comparison.png")

    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
