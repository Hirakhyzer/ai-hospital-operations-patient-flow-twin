"""Plotting helpers for synthetic hospital operations outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_arrivals_by_hour(arrivals: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    arrivals["arrival_hour"].value_counts().sort_index().plot(kind="line", ax=ax)
    ax.set_title("Synthetic arrivals by hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Arrivals")
    _save(fig, path)


def plot_capacity_pressure(capacity: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    capacity.set_index("unit_id")["capacity_pressure_score"].sort_values(ascending=False).plot(kind="bar", ax=ax)
    ax.set_title("Capacity pressure by unit")
    ax.set_xlabel("Unit")
    ax.set_ylabel("Pressure score")
    _save(fig, path)


def plot_staff_workload(staffing: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    staffing.set_index("unit_id")["staff_workload_score"].sort_values(ascending=False).plot(kind="bar", ax=ax)
    ax.set_title("Staff workload by unit")
    ax.set_xlabel("Unit")
    ax.set_ylabel("Workload score")
    _save(fig, path)


def plot_delay_bottlenecks(delay: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    delay.set_index("unit_id")["delay_bottleneck_score"].sort_values(ascending=False).plot(kind="bar", ax=ax)
    ax.set_title("Delay bottleneck score by unit")
    ax.set_xlabel("Unit")
    ax.set_ylabel("Delay score")
    _save(fig, path)


def plot_equity_gap(equity: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    equity.head(12).set_index("group_value")["relative_wait_ratio"].plot(kind="bar", ax=ax)
    ax.set_title("Largest synthetic wait-time ratios")
    ax.set_xlabel("Group")
    ax.set_ylabel("Relative wait ratio")
    ax.tick_params(axis="x", rotation=35)
    _save(fig, path)


def plot_scenario_comparison(comparison: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    comparison.set_index("strategy")["strategy_rank_score"].plot(kind="bar", ax=ax)
    ax.set_title("Scenario strategy rank score")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Rank score")
    ax.tick_params(axis="x", rotation=30)
    _save(fig, path)
