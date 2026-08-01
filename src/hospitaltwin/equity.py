"""Synthetic wait-time equity audit."""

from __future__ import annotations

import pandas as pd


def audit_equity(arrivals: pd.DataFrame) -> pd.DataFrame:
    """Audit synthetic wait-time burdens by access, language, age, and arrival mode."""
    groups = []
    dimensions = ["access_band", "language_access", "age_group", "arrival_mode"]
    overall_wait = float(arrivals["wait_minutes"].mean()) if not arrivals.empty else 0.0
    for dimension in dimensions:
        grouped = arrivals.groupby(dimension).agg(
            patient_count=("patient_id", "count"),
            mean_wait_minutes=("wait_minutes", "mean"),
            p90_wait_minutes=("wait_minutes", lambda s: float(s.quantile(0.90))),
            admitted_rate=("admitted", "mean"),
            mean_severity=("severity_level", "mean"),
        ).reset_index().rename(columns={dimension: "group_value"})
        grouped["dimension"] = dimension
        groups.append(grouped)
    result = pd.concat(groups, ignore_index=True) if groups else pd.DataFrame()
    if result.empty:
        return result
    result["wait_gap_vs_overall_minutes"] = (result["mean_wait_minutes"] - overall_wait).round(3)
    result["relative_wait_ratio"] = (result["mean_wait_minutes"] / max(1.0, overall_wait)).round(4)
    result["equity_review_flag"] = result["relative_wait_ratio"].ge(1.18) & result["patient_count"].ge(8)
    result["equity_note"] = result["equity_review_flag"].map({True: "review_wait_time_burden", False: "within_synthetic_monitoring_band"})
    cols = ["dimension", "group_value", "patient_count", "mean_wait_minutes", "p90_wait_minutes", "wait_gap_vs_overall_minutes", "relative_wait_ratio", "admitted_rate", "mean_severity", "equity_review_flag", "equity_note"]
    return result[cols].sort_values("relative_wait_ratio", ascending=False).reset_index(drop=True)


def equity_summary(audit: pd.DataFrame) -> dict[str, int | float]:
    if audit.empty:
        return {"equity_review_group_count": 0, "max_relative_wait_ratio": 0.0}
    return {
        "equity_review_group_count": int(audit["equity_review_flag"].sum()),
        "max_relative_wait_ratio": float(audit["relative_wait_ratio"].max()),
        "max_wait_gap_vs_overall_minutes": float(audit["wait_gap_vs_overall_minutes"].max()),
    }
