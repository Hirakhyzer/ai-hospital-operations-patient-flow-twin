"""Delay and bottleneck auditing for synthetic hospital operations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def audit_delays(arrivals: pd.DataFrame, handoffs: pd.DataFrame, or_queue: pd.DataFrame, capacity: pd.DataFrame) -> pd.DataFrame:
    """Summarize operational delay bottlenecks."""
    arrival_delay = arrivals.groupby("target_unit_id").agg(
        mean_wait_minutes=("wait_minutes", "mean"),
        p90_wait_minutes=("wait_minutes", lambda s: float(np.percentile(s, 90))),
        arrival_count=("patient_id", "count"),
    ).reset_index().rename(columns={"target_unit_id": "unit_id"})
    handoff = handoffs.merge(arrivals[["patient_id", "target_unit_id"]], on="patient_id", how="left").groupby("target_unit_id").agg(
        ambulance_handoffs=("handoff_id", "count"),
        mean_offload_delay=("offload_delay_minutes", "mean"),
        delayed_handoff_count=("handoff_risk_flag", "sum"),
    ).reset_index().rename(columns={"target_unit_id": "unit_id"}) if not handoffs.empty else pd.DataFrame(columns=["unit_id", "ambulance_handoffs", "mean_offload_delay", "delayed_handoff_count"])
    operating = or_queue.merge(arrivals[["patient_id", "target_unit_id"]], on="patient_id", how="left").groupby("target_unit_id").agg(
        or_cases=("case_id", "count"),
        mean_or_delay_hours=("scheduled_delay_hours", "mean"),
        urgent_cases=("urgency_level", lambda s: int((s >= 3).sum())),
    ).reset_index().rename(columns={"target_unit_id": "unit_id"}) if not or_queue.empty else pd.DataFrame(columns=["unit_id", "or_cases", "mean_or_delay_hours", "urgent_cases"])
    merged = capacity[["unit_id", "unit_type", "discharge_pressure_score", "capacity_pressure_score"]].merge(arrival_delay, on="unit_id", how="left").merge(handoff, on="unit_id", how="left").merge(operating, on="unit_id", how="left").fillna(0)

    rows = []
    for item in merged.itertuples(index=False):
        handoff_component = min(1.0, float(item.mean_offload_delay) / 75.0)
        wait_component = min(1.0, float(item.p90_wait_minutes) / 180.0)
        or_component = min(1.0, float(item.mean_or_delay_hours) / 24.0)
        score = float(np.clip(0.36 * wait_component + 0.24 * handoff_component + 0.20 * or_component + 0.20 * item.discharge_pressure_score, 0, 1.5))
        rows.append({
            "unit_id": item.unit_id,
            "unit_type": item.unit_type,
            "mean_wait_minutes": round(float(item.mean_wait_minutes), 3),
            "p90_wait_minutes": round(float(item.p90_wait_minutes), 3),
            "ambulance_handoffs": int(item.ambulance_handoffs),
            "mean_offload_delay_minutes": round(float(item.mean_offload_delay), 3),
            "delayed_handoff_count": int(item.delayed_handoff_count),
            "or_cases": int(item.or_cases),
            "mean_or_delay_hours": round(float(item.mean_or_delay_hours), 3),
            "discharge_pressure_score": round(float(item.discharge_pressure_score), 4),
            "delay_bottleneck_score": round(score, 4),
            "delay_bottleneck_band": _band(score),
            "primary_delay_driver": _driver(wait_component, handoff_component, or_component, float(item.discharge_pressure_score)),
        })
    return pd.DataFrame(rows).sort_values("delay_bottleneck_score", ascending=False).reset_index(drop=True)


def delay_summary(audit: pd.DataFrame) -> dict[str, int | float]:
    if audit.empty:
        return {"high_delay_bottleneck_unit_count": 0, "mean_delay_bottleneck_score": 0.0}
    return {
        "high_delay_bottleneck_unit_count": int(audit["delay_bottleneck_band"].isin(["high", "critical"]).sum()),
        "mean_delay_bottleneck_score": float(audit["delay_bottleneck_score"].mean()),
        "max_p90_wait_minutes": float(audit["p90_wait_minutes"].max()),
        "total_delayed_handoffs": int(audit["delayed_handoff_count"].sum()),
    }


def _band(score: float) -> str:
    if score >= 1.05:
        return "critical"
    if score >= 0.78:
        return "high"
    if score >= 0.45:
        return "moderate"
    return "low"


def _driver(wait: float, handoff: float, or_delay: float, discharge: float) -> str:
    values = {
        "waiting_room_queue": wait,
        "ambulance_handoff": handoff,
        "operating_room_queue": or_delay,
        "discharge_or_transfer_block": discharge,
    }
    return max(values, key=values.get)
