from pathlib import Path
import json, subprocess, sys
import pandas as pd
import streamlit as st
import plotly.express as px

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

st.set_page_config(
    page_title="Workforce Planner",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Workforce Demand Forecasting & Skill Gap Analysis")
st.caption(
    "Synthetic demonstration data • Fixed seed: 20261022 • "
    "Decision support, not an HR decision-maker"
)


def load_csv(name):
    p = DATA / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


if not (DATA / "employees.csv").exists():
    st.warning("No data found. Generate starter data first.")

    if st.button("Generate starter dataset"):
        subprocess.run(
            [
                sys.executable,
                str(BASE / "src" / "data_generator.py"),
                "--scale",
                "starter",
                "--seed",
                "20261022",
                "--output",
                str(DATA)
            ],
            check=True
        )
        st.rerun()

    st.stop()


employees = load_csv("employees")
roles = load_csv("roles")
skills = load_csv("skills")
employee_skills = load_csv("employee_skills")
projects = load_csv("projects")
demand = load_csv("demand_plans")
demand_skills = load_csv("demand_skills")
allocations = load_csv("allocations")
availability = load_csv("availability")
training = load_csv("training")
gaps = load_csv("gap_analysis")

gt_path = DATA / "ground_truth.json"

ground_truth = (
    json.loads(gt_path.read_text())
    if gt_path.exists()
    else []
)


allocated = (
    allocations.groupby(
        ["employee_id", "period_start"],
        as_index=False
    ).allocated_hours.sum()
    if len(allocations)
    else pd.DataFrame(
        columns=[
            "employee_id",
            "period_start",
            "allocated_hours"
        ]
    )
)


util = availability.merge(
    allocated,
    on=["employee_id", "period_start"],
    how="left"
)

util["allocated_hours"] = util.allocated_hours.fillna(0)

util["utilization_pct"] = (
    util.allocated_hours
    / util.net_capacity_hours.replace(0, pd.NA)
    * 100
).fillna(0)

util["over_capacity"] = (
    util.allocated_hours > util.net_capacity_hours
)


c1, c2, c3, c4 = st.columns(4)

c1.metric("Employees", f"{len(employees):,}")
c2.metric("Projects", f"{len(projects):,}")
c3.metric("Demand records", f"{len(demand):,}")

c4.metric(
    "Skill gaps",
    f"{int((gaps.gap_people > 0).sum()):,}"
    if len(gaps)
    else "0"
)


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Overview",
        "Demand forecast",
        "Skills & gaps",
        "Utilization & exceptions",
        "Data quality"
    ]
)


with tab1:

    st.subheader("Workforce snapshot")

    col1, col2 = st.columns(2)

    with col1:

        role_counts = (
            employees.merge(
                roles[["role_id", "role_name"]],
                on="role_id"
            )
            .groupby("role_name")
            .size()
            .reset_index(name="employees")
        )

        st.plotly_chart(
            px.bar(
                role_counts,
                x="role_name",
                y="employees",
                title="Employees by role"
            ),
            width="stretch"
        )

    with col2:

        monthly = (
            demand.assign(
                period=pd.to_datetime(
                    demand.period_start
                ).dt.to_period("M").astype(str)
            )
            .groupby("period", as_index=False)
            .required_hours.sum()
        )

        st.plotly_chart(
            px.line(
                monthly,
                x="period",
                y="required_hours",
                markers=True,
                title="Monthly demand (hours)"
            ),
            width="stretch"
        )

    st.info(
        "Demand data is synthetic. The monthly curve is generated "
        "planning demand, not a claim of real-world forecast accuracy."
    )


with tab2:

    st.subheader("Demand forecast and planning assumptions")

    if len(demand):

        demand["month"] = (
            pd.to_datetime(demand.period_start)
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            demand.groupby("month", as_index=False)
            .agg(
                demand_hours=("required_hours", "sum"),
                demand_records=("demand_id", "nunique")
            )
        )

        st.dataframe(
            monthly,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download monthly forecast CSV",
            monthly.to_csv(index=False),
            "monthly_demand_forecast.csv",
            "text/csv"
        )

        st.caption(
            "Forecast baseline: generated monthly demand plan. "
            "For predictive validation, replace or supplement this "
            "with historical actual demand and evaluate on a held-out period."
        )

    else:

        st.warning("No demand records.")


with tab3:

    st.subheader("Skill-gap analysis")

    if len(gaps):

        sev = (
            gaps.groupby("severity", as_index=False)
            .size()
        )

        st.plotly_chart(
            px.bar(
                sev,
                x="severity",
                y="size",
                title="Gap records by severity"
            ),
            width="stretch"
        )

        display_gaps = gaps[
            gaps.gap_people > 0
        ].copy()

        st.dataframe(
            display_gaps.head(500),
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download gap analysis CSV",
            gaps.to_csv(index=False),
            "gap_analysis.csv",
            "text/csv"
        )

        st.markdown(
            "**Recommendation rule:** where a demand skill has fewer "
            "currently verified qualified employees than required, "
            "consider internal training or hiring. Validate availability, "
            "role fit, timing, and budget before acting."
        )

    else:

        st.info("No gap records.")


with tab4:

    st.subheader("Utilization and exception handling")

    st.metric(
        "Over-capacity employee-periods",
        int(util.over_capacity.sum())
    )

    st.metric(
        "Average utilization",
        f"{util.utilization_pct.clip(upper=300).mean():.1f}%"
    )

    st.plotly_chart(
        px.histogram(
            util,
            x="utilization_pct",
            nbins=30,
            title="Utilization distribution"
        ),
        width="stretch"
    )

    st.dataframe(
        util[
            util.over_capacity
        ][
            [
                "employee_id",
                "period_start",
                "net_capacity_hours",
                "allocated_hours",
                "utilization_pct"
            ]
        ].head(300),
        width="stretch",
        hide_index=True
    )

    st.subheader("Known injected edge cases (ground truth)")

    if ground_truth:

        st.dataframe(
            pd.DataFrame(ground_truth),
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download ground truth JSON",
            json.dumps(ground_truth, indent=2),
            "ground_truth.json",
            "application/json"
        )

    else:

        st.write("No labelled edge cases found.")


with tab5:

    st.subheader("Data integrity validation")

    report_path = DATA / "validation_summary.json"

    if report_path.exists():

        report = json.loads(
            report_path.read_text()
        )

        st.metric(
            "Validation checks passed",
            f"{report['passed_count']} / {report['total_checks']}"
        )

        st.dataframe(
            pd.DataFrame(report["checks"]),
            width="stretch",
            hide_index=True
        )

    else:

        st.warning(
            "Validation report not found. Run "
            "`python src/validation.py`."
        )

    st.subheader("Dataset table counts")

    counts = [
        {
            "table": p.stem,
            "rows": len(pd.read_csv(p))
        }
        for p in DATA.glob("*.csv")
        if p.name != "validation_summary.csv"
    ]

    st.dataframe(
        pd.DataFrame(counts),
        width="stretch",
        hide_index=True
    )

    st.caption(
        "Ground-truth labels are kept separate from model inputs "
        "and are used to validate exception detection."
    )