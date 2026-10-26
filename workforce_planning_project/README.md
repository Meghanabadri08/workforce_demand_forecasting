# Workforce Demand Forecasting & Skill Gap Analysis

A reproducible synthetic-data project for workforce planning. It demonstrates monthly demand planning, skill-gap analysis, employee capacity/utilization, training/hiring recommendations, labelled edge cases, and validation.

## Features
- 10 core entities plus `DemandSkill` bridge table
- Starter and full-scale deterministic synthetic data generation
- Fixed default seed: `20261022`
- 12 months of demand
- Part-time capacity and leave
- Employee skill profiles with verification and expiry dates
- Four labelled exception scenarios: over-capacity allocation, stale skill, duplicate demand, overlapping assignments
- CSV exports, ground-truth JSON, manifest, SQL schema, and validation report
- Streamlit dashboard with overview, demand, gaps, utilization, and data quality tabs

## Requirements
Python 3.10+ recommended.

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python src/data_generator.py --scale starter --seed 20261022 --output data
python src/validation.py
streamlit run app.py
```

If PowerShell blocks activation, run commands with `python -m pip` and your installed Python executable, or use Command Prompt activation: `.venv\\Scripts\\activate.bat`.

## Full-scale data
```powershell
python src/data_generator.py --scale full --seed 20261022 --output data
python src/validation.py
streamlit run app.py
```
The full configuration creates 5,000 employees, 300 skills, 500 projects, and 12 months of demand/availability records. Use starter first to verify the environment.

## Reproducibility
Run the same generator command twice with the same scale and seed. CSV serialization is stable for the same Python/Pandas environment. Compare SHA-256 values in `data/source_manifest.json`. The generator uses NumPy's `default_rng(seed)` and does not access external sources.

## Important business assumptions
- Synthetic employee names and project names are generated placeholders, not real personal data.
- Scheduled hours are approximated as 4 working weeks per month times 40 hours times FTE. A production implementation should use a business calendar.
- Net capacity = scheduled hours - leave hours. Part-time capacity is already represented through FTE; leave is deducted from the resulting scheduled hours.
- Utilization = allocation hours / net capacity for each employee and period.
- A skill is considered currently verified for the gap analysis when its expiry date is on or after the demand period. Stale profiles are retained and flagged, not deleted.
- Gap analysis is an explainable first-pass comparison of demand skill requirements and employee skill profiles. Production decisions should also include employee availability, role fit, location, cost, and project constraints.
- Demand records are synthetic planning demand, not a validated real-world predictive model. A production forecast needs historical actual demand and a held-out evaluation set.
- `ground_truth.json` is a separate evaluation artefact and must not be used as an input feature.
- The current anomaly injector labels the known cases. Some edge cases intentionally create inconsistent operational records so the validation/dashboard can demonstrate exception handling; these are not presented as clean baseline rows.

## Data dictionary overview
| Table | Key | Main fields |
|---|---|---|
| employees | employee_id | role_id, department, FTE, employment status, location |
| roles | role_id | role name, role family, status |
| skills | skill_id | skill name, category, validity months |
| employee_skills | employee_skill_id | employee_id, skill_id, proficiency, verification and expiry dates |
| projects | project_id | dates, status, priority |
| demand_plans | demand_id | project, role, period, required hours, status |
| demand_skills | demand_skill_id | demand, skill, minimum proficiency, required people |
| allocations | allocation_id | employee, project, period, allocated hours |
| availability | availability_id | employee, period, scheduled, leave, net capacity |
| training | training_id | employee, skill, training period, hours, status |
| gap_analysis | gap_id | demand, skill, shortage, severity, recommended action |

See `schema/data_dictionary.csv` for field-level details and `src/schema.sql` for relational constraints.

## Validation
```powershell
python src/validation.py
```
The report is written to `data/validation_summary.json`. Primary key, foreign key, enum-range, and arithmetic checks are included. Labelled anomaly rows are expected exception cases and are documented in `data/ground_truth.json`.

## Source manifest and lawful provenance
All records are synthetic and generated locally. No external personal or confidential datasets are used. `data/source_manifest.json` records seed, scale, row counts, and checksums.

## Limitations and next steps
This is a deadline-focused prototype. Demand totals are a planning baseline, not a statistically trained forecasting model. The skill-gap engine can be extended with role-specific skill requirements, a working-day calendar, candidate matching, training cost, hiring lead time, and historical forecast metrics (MAE/RMSE) when actual data is available.
