# Synthetic lab

The default runner creates fictional data and writes CSV, JSON, Markdown, audit, and figure outputs under `outputs/`.

Recommended experiment controls:

```bash
python scripts/run_synthetic_hospital_lab.py --units 10 --arrivals 1200 --hours 96 --seed 42
```
