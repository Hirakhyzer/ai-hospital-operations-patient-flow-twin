# Reproducibility Playbook

This playbook defines how to run, document, and report experiments from the **AI Hospital Operations and Patient Flow Digital Twin**.

## 1. Minimum run record

Every experiment should record:

| Field | Example |
|---|---|
| Run name | `hospital_flow_seed_42_arrivals_1200` |
| Dataset type | synthetic fictional hospital operations data |
| Number of arrivals | `1200` |
| Number of units | `10` |
| Random seed | `42` |
| Scenario set | baseline, discharge acceleration, staffing boost, ICU surge, ambulance smoothing, equity-priority |
| Forecast modules | flow, capacity, staffing, delay, equity, scenario comparison |
| Output directory | `outputs/` |
| Boundary statement | synthetic planning simulator only, not clinical decision support |

## 2. Recommended command

```bash
python scripts/run_synthetic_hospital_lab.py --arrivals 1200 --units 10 --seed 42
```

## 3. Evidence bundle

A complete run should include:

```text
outputs/results/synthetic_hospital_units.csv
outputs/results/synthetic_bed_inventory.csv
outputs/results/synthetic_staff_roster.csv
outputs/results/synthetic_patient_arrivals.csv
outputs/results/synthetic_operating_room_queue.csv
outputs/results/synthetic_ambulance_handoffs.csv
outputs/results/synthetic_patient_flow_forecast.csv
outputs/results/synthetic_capacity_audit.csv
outputs/results/synthetic_staffing_audit.csv
outputs/results/synthetic_delay_bottleneck_audit.csv
outputs/results/synthetic_equity_waittime_audit.csv
outputs/results/synthetic_scenario_comparison.csv
outputs/results/synthetic_hospital_flow_summary.json
outputs/reports/synthetic_hospital_operations_report.md
outputs/audit/hospital_operations_audit_log.jsonl
outputs/figures/
```

## 4. Interpretation rules

- Report flow, capacity, staffing, delay, and equity results together.
- Do not claim real hospital performance from synthetic traces.
- Treat wait-time and workload signals as planning prompts only.
- State all scenario assumptions before comparing strategies.
- Preserve the hash-chained audit log when sharing outputs.
- Include the clinical-safety boundary in any report or presentation.

## 5. Checklist before sharing results

- [ ] Seed and configuration recorded.
- [ ] Synthetic-data boundary stated clearly.
- [ ] Scenario assumptions documented.
- [ ] Equity and wait-time metrics included.
- [ ] Clinical-safety limitations stated.
- [ ] Figures and generated report included.
- [ ] No triage, diagnosis, bed-command, or real-time clinical claim is made.
