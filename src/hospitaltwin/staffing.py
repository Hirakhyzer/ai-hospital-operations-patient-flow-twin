"""Staff workload and coverage audit."""

from __future__ import annotations

import numpy as np
import pandas as pd


def audit_staffing(staff: pd.DataFrame, flow: pd.DataFrame) -> pd.DataFrame:
    """Estimate staffing workload pressure by unit."""
    roster = staff.groupby(["unit_id", "unit_type"]).agg(
        scheduled_staff=("scheduled_staff", "sum"),
        available_staff=("available_staff", "sum"),
        sick_callouts=("sick_callouts", "sum"),
    ).reset_index()
    merged = roster.merge(flow[["unit_id", "arrivals", "admitted_patients", "queue_pressure_score", "mean_severity"]], on="unit_id", how="left").fillna(0)
    rows = []
    for item in merged.itertuples(index=False):
        total_work_units = float(item.arrivals + 1.8 * item.admitted_patients + 12 * item.queue_pressure_score + 6 * item.mean_severity)
        available = max(1.0, float(item.available_staff))
        patient_to_staff = total_work_units / available
        callout_rate = float(item.sick_callouts / max(1, item.scheduled_staff))
        workload = float(np.clip(0.055 * patient_to_staff + 0.42 * callout_rate + 0.30 * item.queue_pressure_score, 0, 2.0))
        rows.append({
            "unit_id": item.unit_id,
            "unit_type": item.unit_type,
            "scheduled_staff": int(item.scheduled_staff),
            "available_staff": int(item.available_staff),
            "sick_callouts": int(item.sick_callouts),
            "estimated_patient_work_units": round(total_work_units, 3),
            "patient_to_staff_pressure": round(patient_to_staff, 4),
            "callout_rate": round(callout_rate, 4),
            "staff_workload_score": round(workload, 4),
            "staff_workload_band": _band(workload),
            "requires_staffing_review": bool(workload >= 0.78),
        })
    return pd.DataFrame(rows).sort_values("staff_workload_score", ascending=False).reset_index(drop=True)


def staffing_summary(audit: pd.DataFrame) -> dict[str, int | float]:
    if audit.empty:
        return {"high_staff_workload_unit_count": 0, "mean_staff_workload_score": 0.0}
    return {
        "high_staff_workload_unit_count": int(audit["staff_workload_band"].isin(["high", "critical"]).sum()),
        "mean_staff_workload_score": float(audit["staff_workload_score"].mean()),
        "max_patient_to_staff_pressure": float(audit["patient_to_staff_pressure"].max()),
    }


def _band(score: float) -> str:
    if score >= 1.15:
        return "critical"
    if score >= 0.78:
        return "high"
    if score >= 0.45:
        return "moderate"
    return "low"
