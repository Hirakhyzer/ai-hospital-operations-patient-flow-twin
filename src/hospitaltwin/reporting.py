"""Markdown reporting for synthetic hospital operations planning."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_report(path: str | Path, summary: dict, flow: pd.DataFrame, capacity: pd.DataFrame, staffing: pd.DataFrame, delay: pd.DataFrame, equity: pd.DataFrame, comparison: pd.DataFrame) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = [
        "# Synthetic Hospital Operations and Patient Flow Report",
        "",
        "> This report uses fictional synthetic hospital operations data. It is planning support only and must not be used for triage, treatment, bed assignment, discharge decisions, staffing orders, or real-time patient-safety decisions.",
        "",
        "## Summary",
        "",
        _dict_table(summary),
        "",
        "## Highest patient-flow pressure units",
        "",
        flow.head(8).to_markdown(index=False),
        "",
        "## Capacity pressure",
        "",
        capacity.head(8).to_markdown(index=False),
        "",
        "## Staff workload",
        "",
        staffing.head(8).to_markdown(index=False),
        "",
        "## Delay bottlenecks",
        "",
        delay.head(8).to_markdown(index=False),
        "",
        "## Synthetic equity wait-time audit",
        "",
        equity.head(10).to_markdown(index=False),
        "",
        "## Scenario comparison",
        "",
        comparison.to_markdown(index=False),
        "",
        "## Governance note",
        "",
        "Every output is a planning signal. Real hospital operations require validated data, privacy governance, clinical leadership, administrative authority, and local policy review.",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def _dict_table(summary: dict) -> str:
    return pd.DataFrame([{"metric": key, "value": value} for key, value in summary.items()]).to_markdown(index=False)
