from hospitaltwin.capacity import audit_capacity
from hospitaltwin.delays import audit_delays
from hospitaltwin.equity import audit_equity
from hospitaltwin.flow import forecast_patient_flow
from hospitaltwin.scenarios import compare_strategies
from hospitaltwin.staffing import audit_staffing
from hospitaltwin.synthetic import SyntheticHospitalConfig, generate_synthetic_hospital_data


def test_hospital_modules_return_expected_outputs():
    data = generate_synthetic_hospital_data(SyntheticHospitalConfig(units=7, arrivals=180, hours=36, seed=9))
    flow = forecast_patient_flow(data["arrivals"], data["units"], data["beds"])
    capacity = audit_capacity(data["units"], data["beds"], flow, data["or_queue"])
    staffing = audit_staffing(data["staff"], flow)
    delays = audit_delays(data["arrivals"], data["handoffs"], data["or_queue"], capacity)
    equity = audit_equity(data["arrivals"])
    scenarios = compare_strategies(flow, capacity, staffing, delays, equity)

    assert len(flow) == len(data["units"])
    assert len(capacity) == len(data["units"])
    assert len(staffing) == len(data["units"])
    assert len(delays) == len(data["units"])
    assert not equity.empty
    assert not scenarios.empty
    assert capacity["capacity_pressure_score"].between(0, 2).all()
    assert staffing["staff_workload_score"].between(0, 2).all()
    assert scenarios["strategy_rank_score"].between(0, 1).all()
