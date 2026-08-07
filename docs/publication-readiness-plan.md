# Publication Readiness Plan

This document outlines how the **AI Hospital Operations and Patient Flow Digital Twin** can be framed as an academic research project.

## 1. Possible paper framing

A suitable title could be:

> A Synthetic Hospital Operations Digital Twin for Patient-Flow Forecasting, Capacity Pressure Review, and Responsible Scenario Planning

## 2. Research questions

- Can synthetic patient-flow simulation reproduce interpretable operational pressure signals?
- Which scenarios reduce capacity stress, ambulance handoff delays, or discharge bottlenecks?
- How should staffing workload and wait-time equity be reported together?
- Can hospital operations experiments remain reproducible and auditable without real patient data?

## 3. Suggested experiments

| Experiment | Evidence |
|---|---|
| Baseline flow simulation | Demand, waiting pressure, bed occupancy |
| Scenario comparison | Baseline vs staffing boost vs discharge acceleration vs ICU surge |
| Delay analysis | Ambulance handoffs, diagnostic waiting, transfer delays, discharge blockers |
| Staffing stress test | Workload scores and coverage gaps |
| Equity audit | Synthetic wait-time burden by access group |
| Reproducibility check | Fixed seed, CSV outputs, reports, and audit ledger |

## 4. Required limitations section

Any paper or project report should state that:

- The dataset is synthetic.
- The system is not clinical decision support.
- Operational scores are planning prompts, not patient-level directives.
- Real deployment requires hospital governance, privacy review, clinical validation, and local policy.

## 5. Future extension path

- Add calibrated discrete-event simulation.
- Compare interpretable baselines with time-series forecasting models.
- Add uncertainty intervals around bed and staffing forecasts.
- Add fairness-aware scenario comparison.
- Add privacy-preserving hospital operations analytics.
