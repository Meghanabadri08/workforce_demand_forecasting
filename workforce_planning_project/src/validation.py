import json, hashlib
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"

FK_RULES = {
    "employee_skills": [("employee_id","employees","employee_id"),("skill_id","skills","skill_id")],
    "demand_plans": [("project_id","projects","project_id"),("role_id","roles","role_id")],
    "demand_skills": [("demand_id","demand_plans","demand_id"),("skill_id","skills","skill_id")],
    "allocations": [("employee_id","employees","employee_id"),("project_id","projects","project_id")],
    "availability": [("employee_id","employees","employee_id")],
    "training": [("employee_id","employees","employee_id"),("skill_id","skills","skill_id")],
    "gap_analysis": [("demand_id","demand_plans","demand_id"),("skill_id","skills","skill_id")]
}
PKS = {"employees":"employee_id","roles":"role_id","skills":"skill_id","employee_skills":"employee_skill_id",
       "projects":"project_id","demand_plans":"demand_id","demand_skills":"demand_skill_id",
       "allocations":"allocation_id","availability":"availability_id","training":"training_id","gap_analysis":"gap_id"}

def validate(data_dir=DATA):
    data_dir = Path(data_dir)
    tables = {p.stem:pd.read_csv(p) for p in data_dir.glob("*.csv")}
    checks = []
    for table, pk in PKS.items():
        df = tables.get(table)
        if df is None:
            checks.append({"check":f"{table} exists","passed":False,"details":"Missing CSV"})
            continue
        checks.append({"check":f"{table} primary key unique","passed":bool(df[pk].notna().all() and not df[pk].duplicated().any()),
                       "details":f"{len(df)} rows"})
    for child, rules in FK_RULES.items():
        if child not in tables: continue
        for col, parent, pcol in rules:
            ok = parent in tables and tables[child][col].isin(tables[parent][pcol]).all()
            checks.append({"check":f"{child}.{col} -> {parent}.{pcol}","passed":bool(ok),"details":"foreign key integrity"})
    if "employee_skills" in tables:
        es = tables["employee_skills"]
        checks.append({"check":"proficiency within 1..5","passed":bool(es.proficiency.between(1,5).all()),"details":"allowed proficiency scale"})
    if "availability" in tables:
        av = tables["availability"]
        checks.append({"check":"capacity arithmetic","passed":bool((av.net_capacity_hours - (av.scheduled_hours-av.leave_hours)).abs().max() < 1e-6),"details":"scheduled minus leave"})
    if "allocations" in tables:
        a = tables["allocations"]
        checks.append({"check":"allocation hours non-negative","passed":bool((a.allocated_hours >= 0).all()),"details":"all allocation rows"})
    if "demand_plans" in tables:
        d = tables["demand_plans"]
        checks.append({"check":"demand hours positive","passed":bool((d.required_hours > 0).all()),"details":"all demand rows"})
    result = {"passed":all(x["passed"] for x in checks),"checks":checks,"passed_count":sum(x["passed"] for x in checks),"total_checks":len(checks)}
    (data_dir/"validation_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result

if __name__ == "__main__":
    result = validate()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
