"""Bed, ICU, OR, and discharge capacity audits."""

from __future__ import annotations

import numpy as np
import pandas as pd


def audit_capacity(units: pd.DataFrame, beds: pd.DataFrame, flow: pd.DataFrame, or_queue: pd.DataFrame) -> pd.DataFrame:
    """Audit capacity pressure across hospital units."""
    merged = units.merge(beds, on=["unit_id", "unit_type"], how="left").merge(
        flow[["unit_id", "expected_bed_demand", "queue_pressure_score", "mean_wait_minutes"]], on="unit_id", how="left"
    ).fillna(0)
    or_backlog_hours = float(or_queue["scheduled_delay_hours"].sum()) if not or_queue.empty else 0.0
    rows = []
    for item in merged.itertuples(index=False):
        usable_beds = max(1, int(item.licensed_beds) - int(item.beds_under_maintenance) + int(item.surge_beds))
        occupancy = float(item.occupied_beds / max(1, item.licensed_beds))
        demand_pressure = float(item.expected_bed_demand / usable_beds)
        discharge_pressure = float(item.discharge_friction * 0.7 + item.transfer_dependency * 0.3)
        icu_modifier = 0.18 if item.unit_type == "ICU" else 0.0
        or_modifier = min(0.25, or_backlog_hours / 500) if item.unit_type == "operating_room" else 0.0
        score = float(np.clip(0.34 * occupancy + 0.32 * demand_pressure + 0.22 * discharge_pressure + icu_modifier + or_modifier, 0, 2.0))
        rows.append({
            "unit_id": item.unit_id,
            "unit_type": item.unit_type,
            "licensed_beds": int(item.licensed_beds),
            "occupied_beds": int(item.occupied_beds),
            "usable_beds_with_surge": int(usable_beds),
            "occupancy_rate": round(occupancy, 4),
            "expected_bed_demand": round(float(item.expected_bed_demand), 3),
            "discharge_pressure_score": round(discharge_pressure, 4),
            "capacity_pressure_score": round(score, 4),
            "capacity_pressure_band": _band(score),
            "requires_capacity_review": bool(score >= 0.85),
        })
    return pd.DataFrame(rows).sort_values("capacity_pressure_score", ascending=False).reset_index(drop=True)


def capacity_summary(capacity: pd.DataFrame) -> dict[str, int | float]:
    if capacity.empty:
        return {"critical_capacity_unit_count": 0, "mean_capacity_pressure_score": 0.0}
    return {
        "critical_capacity_unit_count": int(capacity["capacity_pressure_band"].eq("critical").sum()),
        "high_capacity_unit_count": int(capacity["capacity_pressure_band"].isin(["high", "critical"]).sum()),
        "mean_capacity_pressure_score": float(capacity["capacity_pressure_score"].mean()),
        "max_occupancy_rate": float(capacity["occupancy_rate"].max()),
    }


def _band(score: float) -> str:
    if score >= 1.10:
        return "critical"
    if score >= 0.85:
        return "high"
    if score >= 0.55:
        return "moderate"
    return "low"
