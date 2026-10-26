PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS Employee (
 employee_id TEXT PRIMARY KEY, employee_name TEXT NOT NULL, role_id TEXT NOT NULL,
 department TEXT NOT NULL, fte REAL NOT NULL CHECK(fte > 0 AND fte <= 1),
 weekly_hours REAL NOT NULL CHECK(weekly_hours > 0), employment_status TEXT NOT NULL,
 location TEXT NOT NULL, hire_date TEXT NOT NULL,
 FOREIGN KEY(role_id) REFERENCES Role(role_id)
);
CREATE TABLE IF NOT EXISTS Role (
 role_id TEXT PRIMARY KEY, role_name TEXT NOT NULL UNIQUE, role_family TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS Skill (
 skill_id TEXT PRIMARY KEY, skill_name TEXT NOT NULL UNIQUE, category TEXT NOT NULL,
 validity_months INTEGER NOT NULL CHECK(validity_months > 0), status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS EmployeeSkill (
 employee_skill_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, skill_id TEXT NOT NULL,
 proficiency INTEGER NOT NULL CHECK(proficiency BETWEEN 1 AND 5), last_verified_date TEXT NOT NULL,
 expiry_date TEXT NOT NULL, verification_status TEXT NOT NULL,
 FOREIGN KEY(employee_id) REFERENCES Employee(employee_id), FOREIGN KEY(skill_id) REFERENCES Skill(skill_id)
);
CREATE TABLE IF NOT EXISTS Project (
 project_id TEXT PRIMARY KEY, project_name TEXT NOT NULL, client_group TEXT NOT NULL,
 start_date TEXT NOT NULL, end_date TEXT NOT NULL, status TEXT NOT NULL, priority TEXT NOT NULL,
 CHECK(start_date <= end_date)
);
CREATE TABLE IF NOT EXISTS DemandPlan (
 demand_id TEXT PRIMARY KEY, project_id TEXT NOT NULL, role_id TEXT NOT NULL,
 period_start TEXT NOT NULL, period_end TEXT NOT NULL, required_hours REAL NOT NULL CHECK(required_hours > 0),
 status TEXT NOT NULL, source_version INTEGER NOT NULL,
 FOREIGN KEY(project_id) REFERENCES Project(project_id), FOREIGN KEY(role_id) REFERENCES Role(role_id)
);
CREATE TABLE IF NOT EXISTS DemandSkill (
 demand_skill_id TEXT PRIMARY KEY, demand_id TEXT NOT NULL, skill_id TEXT NOT NULL,
 minimum_proficiency INTEGER NOT NULL CHECK(minimum_proficiency BETWEEN 1 AND 5),
 required_people INTEGER NOT NULL CHECK(required_people > 0),
 FOREIGN KEY(demand_id) REFERENCES DemandPlan(demand_id), FOREIGN KEY(skill_id) REFERENCES Skill(skill_id)
);
CREATE TABLE IF NOT EXISTS Allocation (
 allocation_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, project_id TEXT NOT NULL,
 period_start TEXT NOT NULL, period_end TEXT NOT NULL, allocated_hours REAL NOT NULL CHECK(allocated_hours >= 0),
 allocation_status TEXT NOT NULL, event_version INTEGER NOT NULL,
 FOREIGN KEY(employee_id) REFERENCES Employee(employee_id), FOREIGN KEY(project_id) REFERENCES Project(project_id)
);
CREATE TABLE IF NOT EXISTS Availability (
 availability_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL,
 scheduled_hours REAL NOT NULL, leave_hours REAL NOT NULL, net_capacity_hours REAL NOT NULL,
 availability_status TEXT NOT NULL,
 FOREIGN KEY(employee_id) REFERENCES Employee(employee_id),
 CHECK(net_capacity_hours >= 0), CHECK(leave_hours >= 0)
);
CREATE TABLE IF NOT EXISTS Training (
 training_id TEXT PRIMARY KEY, employee_id TEXT NOT NULL, skill_id TEXT NOT NULL,
 planned_start TEXT NOT NULL, planned_end TEXT NOT NULL, hours REAL NOT NULL CHECK(hours > 0),
 status TEXT NOT NULL, outcome_proficiency INTEGER,
 FOREIGN KEY(employee_id) REFERENCES Employee(employee_id), FOREIGN KEY(skill_id) REFERENCES Skill(skill_id)
);
CREATE TABLE IF NOT EXISTS GapAnalysis (
 gap_id TEXT PRIMARY KEY, demand_id TEXT NOT NULL, skill_id TEXT NOT NULL, required_people INTEGER NOT NULL,
 qualified_employee_count INTEGER NOT NULL, gap_people INTEGER NOT NULL, severity TEXT NOT NULL,
 recommended_action TEXT NOT NULL, analysis_date TEXT NOT NULL,
 FOREIGN KEY(demand_id) REFERENCES DemandPlan(demand_id), FOREIGN KEY(skill_id) REFERENCES Skill(skill_id)
);
