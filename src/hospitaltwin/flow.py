"""Patient-flow forecasting for synthetic hospital operations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def forecast_patient_flow(arrivals: pd.DataFrame, units: pd.DataFrame, beds: pd.DataFrame) -> pd.DataFrame:
    """Estimate demand, waits, admissions, and queue pressure by unit."""
    grouped = arrivals.groupby("target_unit_id").agg(
        arrivals=("patient_id", "count"),
        admitted_patients=("admitted", "sum"),
        mean_wait_minutes=("wait_minutes", "mean"),
        p90_wait_minutes=("wait_minutes", lambda s: float(np.percentile(s, 90))),
        mean_severity=("severity_level", "mean"),
        ambulance_arrivals=("arrival_mode", lambda s: int((s == "ambulance").sum())),
        older_adult_count=("age_group", lambda s: int((s == "older_adult").sum())),
    ).reset_index().rename(columns={"target_unit_id": "unit_id"})

    merged = units.merge(beds, on=["unit_id", "unit_type"], how="left").merge(grouped, on="unit_id", how="left").fillna(0)
    rows = []
    for unit in merged.itertuples(index=False):
        expected_bed_demand = float(unit.admitted_patients + 0.18 * unit.arrivals + 0.10 * unit.older_adult_count)
        available_capacity = float(max(1, unit.available_beds + unit.surge_beds - unit.beds_under_maintenance))
        queue_pressure = float(np.clip((expected_bed_demand / available_capacity) * 0.62 + (unit.mean_wait_minutes / 180) * 0.38, 0, 2.5))
        rows.append({
            "unit_id": unit.unit_id,
            "unit_type": unit.unit_type,
            "arrivals": int(unit.arrivals),
            "admitted_patients": int(unit.admitted_patients),
            "mean_wait_minutes": round(float(unit.mean_wait_minutes), 3),
            "p90_wait_minutes": round(float(unit.p90_wait_minutes), 3),
            "mean_severity": round(float(unit.mean_severity), 3),
            "ambulance_arrivals": int(unit.ambulance_arrivals),
            "available_beds_after_maintenance": int(max(0, unit.available_beds - unit.beds_under_maintenance)),
            "surge_beds": int(unit.surge_beds),
            "expected_bed_demand": round(expected_bed_demand, 3),
            "queue_pressure_score": round(queue_pressure, 4),
            "flow_pressure_band": _band(queue_pressure),
        })
    return pd.DataFrame(rows).sort_values("queue_pressure_score", ascending=False).reset_index(drop=True)


def flow_summary(flow: pd.DataFrame) -> dict[str, int | float]:
    if flow.empty:
        return {"high_flow_pressure_unit_count": 0, "mean_queue_pressure_score": 0.0}
    return {
        "high_flow_pressure_unit_count": int(flow["flow_pressure_band"].isin(["high", "critical"]).sum()),
        "mean_queue_pressure_score": float(flow["queue_pressure_score"].mean()),
        "total_synthetic_arrivals": int(flow["arrivals"].sum()),
        "total_expected_bed_demand": float(flow["expected_bed_demand"].sum()),
    }


def _band(score: float) -> str:
    if score >= 1.25:
        return "critical"
    if score >= 0.90:
        return "high"
    if score >= 0.55:
        return "moderate"
    return "low"
