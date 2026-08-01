"""Scenario comparison for synthetic hospital operations."""

from __future__ import annotations

import numpy as np
import pandas as pd


STRATEGIES = {
    "baseline": {"capacity": 1.00, "staff": 1.00, "delay": 1.00, "equity": 1.00},
    "discharge_acceleration": {"capacity": 0.82, "staff": 0.96, "delay": 0.86, "equity": 0.94},
    "staffing_boost": {"capacity": 0.94, "staff": 0.72, "delay": 0.88, "equity": 0.91},
    "icu_surge": {"capacity": 0.74, "staff": 0.92, "delay": 0.90, "equity": 0.96},
    "ambulance_smoothing": {"capacity": 0.95, "staff": 0.98, "delay": 0.70, "equity": 0.92},
    "equity_priority": {"capacity": 0.91, "staff": 0.94, "delay": 0.84, "equity": 0.68},
}


def compare_strategies(flow: pd.DataFrame, capacity: pd.DataFrame, staffing: pd.DataFrame, delay: pd.DataFrame, equity: pd.DataFrame) -> pd.DataFrame:
    """Compare transparent hospital operations strategies."""
    base_capacity = float(capacity["capacity_pressure_score"].mean()) if not capacity.empty else 0.0
    base_staff = float(staffing["staff_workload_score"].mean()) if not staffing.empty else 0.0
    base_delay = float(delay["delay_bottleneck_score"].mean()) if not delay.empty else 0.0
    base_equity = float(max(0.0, equity["relative_wait_ratio"].max() - 1.0)) if not equity.empty else 0.0
    arrivals = int(flow["arrivals"].sum()) if not flow.empty else 0
    rows = []
    for name, multipliers in STRATEGIES.items():
        capacity_score = base_capacity * multipliers["capacity"]
        staff_score = base_staff * multipliers["staff"]
        delay_score = base_delay * multipliers["delay"]
        equity_gap = base_equity * multipliers["equity"]
        composite = float(np.clip(0.34 * capacity_score + 0.25 * staff_score + 0.25 * delay_score + 0.16 * equity_gap, 0, 2.0))
        rows.append({
            "strategy": name,
            "synthetic_arrivals_evaluated": arrivals,
            "projected_capacity_pressure": round(capacity_score, 4),
            "projected_staff_workload": round(staff_score, 4),
            "projected_delay_bottleneck": round(delay_score, 4),
            "projected_equity_gap": round(equity_gap, 4),
            "composite_operations_risk": round(composite, 4),
            "strategy_rank_score": round(1 / (1 + composite), 4),
            "planning_note": _note(name),
        })
    return pd.DataFrame(rows).sort_values("strategy_rank_score", ascending=False).reset_index(drop=True)


def scenario_summary(comparison: pd.DataFrame) -> dict[str, int | float | str]:
    if comparison.empty:
        return {"best_strategy": "none", "best_strategy_rank_score": 0.0}
    best = comparison.iloc[0]
    return {
        "best_strategy": str(best["strategy"]),
        "best_strategy_rank_score": float(best["strategy_rank_score"]),
        "lowest_composite_operations_risk": float(best["composite_operations_risk"]),
    }


def _note(name: str) -> str:
    return {
        "baseline": "current synthetic operating posture",
        "discharge_acceleration": "prioritize discharge coordination and downstream placement",
        "staffing_boost": "add flexible staff to overloaded units",
        "icu_surge": "expand critical-care capacity and respiratory support",
        "ambulance_smoothing": "reduce ambulance offload delay and ED entry bottlenecks",
        "equity_priority": "prioritize groups with higher synthetic wait-time burden",
    }[name]
