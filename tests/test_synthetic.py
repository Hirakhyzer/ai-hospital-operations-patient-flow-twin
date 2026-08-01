from hospitaltwin.synthetic import SyntheticHospitalConfig, generate_synthetic_hospital_data


def test_synthetic_generator_shapes():
    data = generate_synthetic_hospital_data(SyntheticHospitalConfig(units=6, arrivals=120, hours=24, seed=3))
    assert len(data["units"]) == 6
    assert len(data["arrivals"]) == 120
    assert {"units", "beds", "staff", "arrivals", "or_queue", "handoffs"} <= set(data)
    assert data["arrivals"]["patient_id"].str.startswith("SP").all()
    assert data["arrivals"]["synthetic_label"].eq("fictional_patient_flow_record").all()
