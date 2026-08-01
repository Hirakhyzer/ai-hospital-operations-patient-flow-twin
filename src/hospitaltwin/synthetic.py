"""Synthetic hospital operations data generator.

All records are fictional and intended for hospital-planning research only.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

UNIT_TYPES = ["ED", "ICU", "medical_surgical", "pediatrics", "observation", "step_down", "operating_room", "imaging"]
ARRIVAL_MODES = ["walk_in", "ambulance", "referral", "transfer"]
ACCESS_BANDS = ["near", "moderate", "far"]
LANGUAGE_SUPPORT = ["standard", "interpreter_needed"]
AGE_GROUPS = ["pediatric", "adult", "older_adult"]


@dataclass(frozen=True)
class SyntheticHospitalConfig:
    units: int = 8
    arrivals: int = 720
    hours: int = 72
    seed: int = 42


def generate_synthetic_hospital_data(config: SyntheticHospitalConfig) -> dict[str, pd.DataFrame]:
    """Generate fictional hospital units, beds, staff, arrivals, OR queues, and ambulance handoffs."""
    rng = np.random.default_rng(config.seed)
    units = _units(config, rng)
    beds = _beds(units, rng)
    staff = _staff(units, rng, config.hours)
    arrivals = _arrivals(config, rng, units)
    or_queue = _or_queue(config, rng, arrivals)
    handoffs = _ambulance_handoffs(rng, arrivals)
    return {
        "units": units,
        "beds": beds,
        "staff": staff,
        "arrivals": arrivals,
        "or_queue": or_queue,
        "handoffs": handoffs,
    }


def _units(config: SyntheticHospitalConfig, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    base_types = UNIT_TYPES.copy()
    while len(base_types) < config.units:
        base_types.append(str(rng.choice(UNIT_TYPES)))
    for idx in range(config.units):
        unit_type = base_types[idx % len(base_types)]
        rows.append({
            "unit_id": f"U{idx + 1:03d}",
            "unit_name": f"Synthetic {unit_type.replace('_', ' ').title()} Unit {idx + 1}",
            "unit_type": unit_type,
            "criticality": int(rng.integers(2, 6)) if unit_type in ["ED", "ICU", "operating_room"] else int(rng.integers(1, 5)),
            "baseline_occupancy_rate": float(np.round(rng.uniform(0.55, 0.94), 3)),
            "discharge_friction": float(np.round(rng.uniform(0.12, 0.72), 3)),
            "transfer_dependency": float(np.round(rng.uniform(0.08, 0.65), 3)),
        })
    return pd.DataFrame(rows)


def _beds(units: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for unit in units.itertuples(index=False):
        if unit.unit_type == "ICU":
            beds = int(rng.integers(10, 34))
        elif unit.unit_type == "ED":
            beds = int(rng.integers(18, 48))
        elif unit.unit_type == "operating_room":
            beds = int(rng.integers(4, 14))
        else:
            beds = int(rng.integers(16, 72))
        occupied = int(np.clip(round(beds * unit.baseline_occupancy_rate + rng.normal(0, 2.2)), 0, beds))
        rows.append({
            "unit_id": unit.unit_id,
            "unit_type": unit.unit_type,
            "licensed_beds": beds,
            "occupied_beds": occupied,
            "available_beds": beds - occupied,
            "surge_beds": int(max(1, round(beds * rng.uniform(0.05, 0.22)))),
            "beds_under_maintenance": int(rng.integers(0, max(1, beds // 8))),
        })
    return pd.DataFrame(rows)


def _staff(units: pd.DataFrame, rng: np.random.Generator, hours: int) -> pd.DataFrame:
    roles = ["nurse", "physician", "respiratory_therapist", "technician", "case_manager"]
    rows = []
    shifts = max(1, hours // 12)
    for unit in units.itertuples(index=False):
        for shift in range(shifts):
            for role in roles:
                base = {"nurse": 6, "physician": 2, "respiratory_therapist": 1, "technician": 2, "case_manager": 1}[role]
                if unit.unit_type in ["ICU", "ED"]:
                    base += 2
                available = max(0, int(rng.poisson(base)))
                rows.append({
                    "shift_id": f"S{shift + 1:03d}",
                    "hour_start": int(shift * 12),
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "role": role,
                    "scheduled_staff": available + int(rng.integers(0, 3)),
                    "available_staff": available,
                    "sick_callouts": int(rng.integers(0, 3)),
                })
    return pd.DataFrame(rows)


def _arrivals(config: SyntheticHospitalConfig, rng: np.random.Generator, units: pd.DataFrame) -> pd.DataFrame:
    rows = []
    unit_ids = units["unit_id"].tolist()
    ed_units = units.loc[units["unit_type"].eq("ED"), "unit_id"].tolist() or [unit_ids[0]]
    icu_units = units.loc[units["unit_type"].eq("ICU"), "unit_id"].tolist() or unit_ids
    for idx in range(config.arrivals):
        hour = int(rng.integers(0, config.hours))
        mode = str(rng.choice(ARRIVAL_MODES, p=[0.52, 0.26, 0.16, 0.06]))
        severity = int(rng.choice([1, 2, 3, 4, 5], p=[0.18, 0.25, 0.31, 0.18, 0.08]))
        if severity >= 4 and rng.random() < 0.34:
            target = str(rng.choice(icu_units))
        elif mode == "ambulance" or severity >= 3:
            target = str(rng.choice(ed_units))
        else:
            target = str(rng.choice(unit_ids))
        access = str(rng.choice(ACCESS_BANDS, p=[0.46, 0.34, 0.20]))
        language = str(rng.choice(LANGUAGE_SUPPORT, p=[0.82, 0.18]))
        age_group = str(rng.choice(AGE_GROUPS, p=[0.15, 0.58, 0.27]))
        base_wait = 18 + 11 * severity + (14 if mode == "ambulance" else 0) + (9 if access == "far" else 0) + (7 if language == "interpreter_needed" else 0)
        wait_minutes = float(np.round(max(3, rng.normal(base_wait, 17)), 2))
        los_hours = float(np.round(max(0.5, rng.gamma(2.2 + severity * 0.35, 2.1)), 2))
        admission_probability = float(np.clip(0.08 + 0.14 * severity + (0.12 if age_group == "older_adult" else 0.0), 0.02, 0.92))
        admitted = bool(rng.random() < admission_probability)
        rows.append({
            "patient_id": f"SP{idx + 1:06d}",
            "arrival_hour": hour,
            "arrival_mode": mode,
            "severity_level": severity,
            "target_unit_id": target,
            "access_band": access,
            "language_access": language,
            "age_group": age_group,
            "wait_minutes": wait_minutes,
            "length_of_stay_hours": los_hours,
            "admitted": admitted,
            "synthetic_label": "fictional_patient_flow_record",
        })
    return pd.DataFrame(rows)


def _or_queue(config: SyntheticHospitalConfig, rng: np.random.Generator, arrivals: pd.DataFrame) -> pd.DataFrame:
    n_cases = max(1, min(len(arrivals), max(10, config.arrivals // 10)))
    surgical = arrivals.sample(n=n_cases, random_state=config.seed)
    rows = []
    for idx, patient in enumerate(surgical.itertuples(index=False)):
        urgency = int(rng.choice([1, 2, 3, 4], p=[0.20, 0.36, 0.30, 0.14]))
        scheduled_delay = float(np.round(max(0.5, rng.gamma(2.0 + urgency * 0.4, 3.2)), 2))
        rows.append({
            "case_id": f"OR{idx + 1:05d}",
            "patient_id": patient.patient_id,
            "request_hour": int(patient.arrival_hour),
            "urgency_level": urgency,
            "estimated_case_hours": float(np.round(rng.uniform(0.8, 5.5), 2)),
            "scheduled_delay_hours": scheduled_delay,
            "post_op_bed_needed": bool(rng.random() < 0.62),
        })
    return pd.DataFrame(rows)


def _ambulance_handoffs(rng: np.random.Generator, arrivals: pd.DataFrame) -> pd.DataFrame:
    ambulance = arrivals[arrivals["arrival_mode"].eq("ambulance")].copy()
    rows = []
    for idx, patient in enumerate(ambulance.itertuples(index=False)):
        offload = float(np.round(max(4, rng.normal(24 + 9 * patient.severity_level, 16)), 2))
        rows.append({
            "handoff_id": f"AH{idx + 1:05d}",
            "patient_id": patient.patient_id,
            "arrival_hour": int(patient.arrival_hour),
            "severity_level": int(patient.severity_level),
            "offload_delay_minutes": offload,
            "crew_clearance_minutes": float(np.round(offload + rng.uniform(5, 32), 2)),
            "handoff_risk_flag": bool(offload > 45),
        })
    return pd.DataFrame(rows)
