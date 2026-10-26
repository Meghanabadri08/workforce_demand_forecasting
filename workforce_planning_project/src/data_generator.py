import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

SEED_DEFAULT = 20261022
ROLES = ["Data Analyst", "Software Engineer", "ML Engineer", "Project Manager", "QA Engineer",
         "Frontend Developer", "Backend Developer", "Cloud Engineer", "Business Analyst", "Cybersecurity Analyst"]
SKILLS = ["Python", "SQL", "Java", "JavaScript", "HTML/CSS", "Machine Learning", "Data Analysis",
          "Cloud", "Testing", "Communication", "Project Management", "Cybersecurity", "React", "Git",
          "Statistics", "Data Visualization", "API Design", "Linux", "Excel", "Docker"]
DEPARTMENTS = ["Engineering", "Data", "Product", "Operations", "Security", "Quality Assurance"]
STATUSES = ["Active", "On Leave", "Inactive"]
PROFICIENCY = [1, 2, 3, 4, 5]

def make_id(prefix, n, width=6):
    return f"{prefix}{n:0{width}d}"

def generate(scale="starter", seed=SEED_DEFAULT, output_dir="data"):
    cfg = {"starter": (100, 20, 10), "full": (5000, 300, 500)}
    if scale not in cfg:
        raise ValueError("scale must be starter or full")
    n_emp, n_skills, n_projects = cfg[scale]
    rng = np.random.default_rng(seed)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    roles_n = min(len(ROLES), max(5, n_emp // 10))
    roles = pd.DataFrame({
        "role_id": [f"ROLE-{i+1:03d}" for i in range(roles_n)],
        "role_name": ROLES[:roles_n],
        "role_family": [x.split()[0] for x in ROLES[:roles_n]],
        "status": "Active"
    })
    skill_names = (SKILLS + [f"Specialized Skill {i:03d}" for i in range(1, n_skills-len(SKILLS)+1)])[:n_skills]
    skills = pd.DataFrame({
        "skill_id": [make_id("SKL-", i+1) for i in range(n_skills)],
        "skill_name": skill_names,
        "category": [("Technical" if i % 4 != 3 else "Professional") for i in range(n_skills)],
        "validity_months": rng.choice([6, 12, 18, 24, 36], n_skills),
        "status": "Active"
    })
    employees = []
    for i in range(1, n_emp+1):
        role_idx = int(rng.integers(0, roles_n))
        fte = float(rng.choice([0.5, 0.6, 0.75, 0.8, 1.0], p=[.05,.05,.1,.1,.7]))
        employees.append({
            "employee_id": make_id("EMP-", i), "employee_name": f"Employee {i:05d}",
            "role_id": roles.iloc[role_idx]["role_id"],
            "department": str(rng.choice(DEPARTMENTS)), "fte": fte,
            "weekly_hours": 40.0, "employment_status": str(rng.choice(STATUSES, p=[.94,.04,.02])),
            "location": str(rng.choice(["Hyderabad", "Bengaluru", "Pune", "Chennai", "Remote"])),
            "hire_date": str(pd.Timestamp("2018-01-01") + pd.Timedelta(days=int(rng.integers(0, 3200))))
        })
    employees = pd.DataFrame(employees)
    projects = []
    for i in range(1, n_projects+1):
        projects.append({
            "project_id": f"PRJ-2026-{i:06d}", "project_name": f"Project {i:04d}",
            "client_group": str(rng.choice(["Internal", "Enterprise", "SMB", "Public Sector"])),
            "start_date": "2026-01-01", "end_date": "2026-12-31",
            "status": str(rng.choice(["Planned", "Active", "On Hold"], p=[.35,.6,.05])),
            "priority": str(rng.choice(["Low", "Medium", "High"], p=[.2,.5,.3]))
        })
    projects = pd.DataFrame(projects)
    # Employee skill profiles: 3-8 profiles per employee, with a verifiable stale subset.
    emp_skills = []
    esn = 1
    skill_ids = skills["skill_id"].tolist()
    for emp in employees.itertuples(index=False):
        count = min(n_skills, int(rng.integers(3, min(8, n_skills)+1)))
        chosen = rng.choice(skill_ids, size=count, replace=False)
        for sid in chosen:
            verified = pd.Timestamp("2026-10-01") - pd.Timedelta(days=int(rng.integers(0, 1000)))
            emp_skills.append({
                "employee_skill_id": f"ES-{esn:08d}", "employee_id": emp.employee_id, "skill_id": sid,
                "proficiency": int(rng.choice(PROFICIENCY, p=[.08,.18,.34,.28,.12])),
                "last_verified_date": verified.date().isoformat(),
                "expiry_date": (verified + pd.DateOffset(months=12)).date().isoformat(),
                "verification_status": "Verified"
            })
            esn += 1
    employee_skills = pd.DataFrame(emp_skills)
    # Demand is monthly for 12 months, role-level hours and skill requirements.
    demand = []
    demand_skill = []
    demand_counter = 1
    ds_counter = 1
    months = pd.date_range("2026-01-01", periods=12, freq="MS")
    for p in projects.itertuples(index=False):
        for month in months:
            n_records = int(rng.integers(1, 4))
            for _ in range(n_records):
                role_id = str(rng.choice(roles["role_id"].tolist()))
                hours = int(rng.choice([40, 80, 120, 160, 240, 320, 480]))
                demand_id = f"DEM-{p.project_id}-{month.strftime('%Y%m')}-{demand_counter:06d}"
                demand.append({
                    "demand_id": demand_id, "project_id": p.project_id, "role_id": role_id,
                    "period_start": month.date().isoformat(), "period_end": (month + pd.offsets.MonthEnd(0)).date().isoformat(),
                    "required_hours": hours, "status": "Approved", "source_version": 1
                })
                skill_id = str(rng.choice(skill_ids))
                demand_skill.append({"demand_skill_id": f"DS-{ds_counter:08d}", "demand_id": demand_id,
                                     "skill_id": skill_id, "minimum_proficiency": int(rng.choice([2,3,4])),
                                     "required_people": max(1, int(np.ceil(hours/160)))})
                demand_counter += 1
                ds_counter += 1
    demand = pd.DataFrame(demand)
    demand_skill = pd.DataFrame(demand_skill)
    # Availability records by employee and month. Leave and capacity are explicitly recorded.
    availability = []
    avn = 1
    for emp in employees.itertuples(index=False):
        for month in months:
            scheduled = float(emp.weekly_hours * 4.0 * emp.fte)
            leave = float(rng.choice([0,0,0,4,8,16,24]))
            net = max(0.0, scheduled - leave)
            availability.append({
                "availability_id": f"AV-{avn:08d}", "employee_id": emp.employee_id,
                "period_start": month.date().isoformat(), "period_end": (month + pd.offsets.MonthEnd(0)).date().isoformat(),
                "scheduled_hours": scheduled, "leave_hours": leave, "net_capacity_hours": net,
                "availability_status": "Available" if net > 0 and emp.employment_status == "Active" else "Unavailable"
            })
            avn += 1
    availability = pd.DataFrame(availability)
    # Valid baseline allocations, one row is employee/project/month; later inject labelled anomalies.
    allocations = []
    al_counter = 1
    active_emp = employees[employees.employment_status == "Active"]
    for emp in active_emp.itertuples(index=False):
        for month in months:
            if rng.random() < 0.25:
                proj = projects.iloc[int(rng.integers(0, len(projects)))]
                cap_row = availability[(availability.employee_id == emp.employee_id) &
                                       (availability.period_start == month.date().isoformat())].iloc[0]
                cap = float(cap_row.net_capacity_hours)
                hours = float(min(cap, rng.choice([8,16,24,32,40,48,64])))
                if hours > 0:
                    allocations.append({
                        "allocation_id": f"ALLOC-2026-{al_counter:08d}", "employee_id": emp.employee_id,
                        "project_id": proj.project_id, "period_start": month.date().isoformat(),
                        "period_end": (month + pd.offsets.MonthEnd(0)).date().isoformat(),
                        "allocated_hours": hours, "allocation_status": "Confirmed", "event_version": 1
                    })
                    al_counter += 1
    allocations = pd.DataFrame(allocations, columns=["allocation_id","employee_id","project_id","period_start","period_end","allocated_hours","allocation_status","event_version"])
    # Training plans, with outcomes represented as lifecycle state.
    training = []
    for i in range(1, max(10, n_emp//5)+1):
        emp = employees.iloc[int(rng.integers(0, n_emp))]
        sk = skills.iloc[int(rng.integers(0, n_skills))]
        training.append({"training_id": f"TRN-{i:08d}", "employee_id": emp.employee_id, "skill_id": sk.skill_id,
                         "planned_start": "2026-11-01", "planned_end": "2026-12-15",
                         "hours": int(rng.choice([4,8,12,16,24,40])),
                         "status": str(rng.choice(["Planned","In Progress","Completed"], p=[.5,.3,.2])),
                         "outcome_proficiency": None})
    training = pd.DataFrame(training)
    # Inject four explicit, traceable edge cases without changing unrelated records.
    ground_truth = []
    issue_num = 1
    if len(allocations) and len(availability):
        row = allocations.iloc[0]
        idx = allocations.index[0]
        caprow = availability[(availability.employee_id == row.employee_id) & (availability.period_start == row.period_start)].iloc[0]
        allocations.loc[idx, "allocated_hours"] = float(caprow.net_capacity_hours + 24)
        ground_truth.append({"issue_id":f"ISS-{issue_num:06d}","issue_type":"ALLOCATION_OVER_CAPACITY","affected_entity":"Allocation","affected_id":row.allocation_id,"expected_result":"Flag allocated hours above net capacity","expected_action":"Reallocate or reduce allocation"}); issue_num += 1
    if len(employee_skills):
        idx = employee_skills.index[0]
        employee_skills.loc[idx, "last_verified_date"] = "2023-01-01"
        employee_skills.loc[idx, "expiry_date"] = "2024-01-01"
        ground_truth.append({"issue_id":f"ISS-{issue_num:06d}","issue_type":"STALE_SKILL_TREATED_CURRENT","affected_entity":"EmployeeSkill","affected_id":employee_skills.loc[idx,"employee_skill_id"],"expected_result":"Mark stale and exclude from verified-qualified capacity","expected_action":"Re-verify or train"}); issue_num += 1
    if len(demand):
        dup = demand.iloc[0].copy()
        dup["demand_id"] = f"DEM-DUP-{issue_num:06d}"
        dup["source_version"] = 1
        demand = pd.concat([demand, pd.DataFrame([dup])], ignore_index=True)
        original = demand.iloc[0]
        ground_truth.append({"issue_id":f"ISS-{issue_num:06d}","issue_type":"DEMAND_DOUBLE_COUNTED","affected_entity":"DemandPlan","affected_id":dup["demand_id"],"expected_result":"Detect duplicate underlying project/role/period demand","expected_action":"Exclude duplicate from forecast total"}); issue_num += 1
        # Skill bridge for duplicated demand is also duplicated with a fresh key.
        dskill = demand_skill[demand_skill.demand_id == original.demand_id]
        if len(dskill):
            copy = dskill.iloc[0].copy()
            copy["demand_skill_id"] = f"DS-{ds_counter:08d}"
            copy["demand_id"] = dup["demand_id"]
            demand_skill = pd.concat([demand_skill, pd.DataFrame([copy])], ignore_index=True)
    if len(active_emp) and len(projects):
        emp = active_emp.iloc[0]
        month = months[0]
        same = allocations[(allocations.employee_id == emp.employee_id) & (allocations.period_start == month.date().isoformat())]
        if len(same):
            original = same.iloc[0]
            new = original.copy()
            new["allocation_id"] = f"ALLOC-2026-{al_counter:08d}"
            new["project_id"] = projects[projects.project_id != original.project_id].iloc[0].project_id if len(projects) > 1 else original.project_id
            new["allocated_hours"] = min(8.0, float(new.allocated_hours))
            allocations = pd.concat([allocations, pd.DataFrame([new])], ignore_index=True)
            ground_truth.append({"issue_id":f"ISS-{issue_num:06d}","issue_type":"OVERLAPPING_PROJECT_ASSIGNMENT","affected_entity":"Allocation","affected_id":new["allocation_id"],"expected_result":"Flag employee assigned to multiple projects in same period","expected_action":"Review schedule and reallocate"}); issue_num += 1
    # Gap analysis is a derived record per demand skill based on current verified profiles.
    gaps = []
    gap_n = 1
    skill_current = employee_skills.copy()
    skill_current["last_verified_date"] = pd.to_datetime(skill_current.last_verified_date)
    skill_current["expiry_date"] = pd.to_datetime(skill_current.expiry_date)
    for ds in demand_skill.itertuples(index=False):
        drow = demand[demand.demand_id == ds.demand_id]
        if drow.empty: continue
        drow = drow.iloc[0]
        qualified_ids = set(skill_current[(skill_current.skill_id == ds.skill_id) &
            (skill_current.proficiency >= ds.minimum_proficiency) &
            (skill_current.expiry_date >= pd.Timestamp(drow.period_start))].employee_id)
        # Use role-qualified employees where possible; this is an explainable first-pass estimate.
        available_count = len(qualified_ids)
        required = int(ds.required_people)
        shortage = max(0, required - min(required, available_count))
        gaps.append({"gap_id":f"GAP-{gap_n:08d}", "demand_id":ds.demand_id, "skill_id":ds.skill_id,
                     "required_people":required, "qualified_employee_count":available_count,
                     "gap_people":shortage, "severity":"High" if shortage >= 2 else ("Medium" if shortage == 1 else "None"),
                     "recommended_action":"Train or hire" if shortage else "No action required",
                     "analysis_date":"2026-10-26"})
        gap_n += 1
    gaps = pd.DataFrame(gaps, columns=["gap_id","demand_id","skill_id","required_people","qualified_employee_count","gap_people","severity","recommended_action","analysis_date"])
    # Persist all data files.
    tables = {
        "employees":employees, "roles":roles, "skills":skills, "employee_skills":employee_skills,
        "projects":projects, "demand_plans":demand, "demand_skills":demand_skill,
        "allocations":allocations, "availability":availability, "training":training, "gap_analysis":gaps
    }
    for name, df in tables.items():
        df.to_csv(out / f"{name}.csv", index=False)
    (out / "ground_truth.json").write_text(json.dumps(ground_truth, indent=2), encoding="utf-8")
    manifest = {"seed":seed,"scale":scale,"generated_on":"2026-10-26","synthetic_only":True,
                "tables":{name:{"rows":len(df),"sha256":hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()} for name,df in tables.items()}}
    (out / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return tables, ground_truth

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scale", choices=["starter","full"], default="starter")
    parser.add_argument("--seed", type=int, default=SEED_DEFAULT)
    parser.add_argument("--output", default="data")
    args = parser.parse_args()
    tables, gt = generate(args.scale, args.seed, args.output)
    print(f"Generated {len(tables)} tables in {args.output}; ground-truth issues: {len(gt)}")
    for name, df in tables.items(): print(f"{name}: {len(df):,} rows")
