import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from reporting.data import generate_sample_data, validate_data
from reporting.metrics import calculate_metrics, department_summary
from reporting.workflow import create_report

load_dotenv()

st.set_page_config(
    page_title="AI Reporting Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("AI-Powered Internal Reporting Assistant")
st.caption(
    "Automated operational analytics and AI-generated management insights"
)

# --------------------------------------------------
# 1. Load sample data or upload a CSV
# --------------------------------------------------
@st.cache_data
def load_demo_data():
    sample_path = Path("data/sample_operations.csv")
    if sample_path.exists():
        return validate_data(pd.read_csv(sample_path))
    return validate_data(generate_sample_data())

with st.sidebar:
    st.header("Report configuration")
    uploaded_file = st.file_uploader(
        "Upload operational data",
        type=["csv"],
        help="CSV must contain the documented reporting columns.",
    )

    st.caption(
        "Demo data is synthetic. Do not upload confidential "
        "company data to this prototype."
    )

try:
    if uploaded_file is not None:
        df = validate_data(pd.read_csv(uploaded_file))
        data_source = "Uploaded CSV"
    else:
        df = load_demo_data()
        data_source = "Synthetic demo data"
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.caption(f"Data source: {data_source} · {len(df):,} records")

# --------------------------------------------------
# 2. Filters
# --------------------------------------------------
with st.sidebar:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    selected_dates = st.date_input(
        "Reporting period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    departments = sorted(df["department"].unique().tolist())
    selected_departments = st.multiselect(
        "Departments",
        options=departments,
        default=departments,
    )

if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates

if start_date > end_date:
    st.error("Start date must be on or before end date.")
    st.stop()

filtered = df[
    df["date"].dt.date.between(start_date, end_date)
    & df["department"].isin(selected_departments)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Adjust your selections.")
    st.stop()

# --------------------------------------------------
# 3. Deterministic KPIs
# --------------------------------------------------
metrics = calculate_metrics(filtered)
dept_summary = department_summary(filtered)

st.subheader("Executive overview")
st.caption(f"{start_date:%d %b %Y} – {end_date:%d %b %Y}")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Revenue", f"${metrics['revenue']:,.0f}")
k2.metric("Operating cost", f"${metrics['cost']:,.0f}")
k3.metric("Profit", f"${metrics['profit']:,.0f}")

margin = metrics["profit_margin_pct"]
k4.metric(
    "Profit margin",
    f"{margin:.1f}%" if margin is not None else "N/A",
)

k5, k6, k7 = st.columns(3)

resolution = metrics["resolution_rate_pct"]
sla = metrics["sla_compliance_pct"]

k5.metric("Tickets opened", f"{metrics['tickets_opened']:,}")
k6.metric(
    "Resolution rate",
    f"{resolution:.1f}%" if resolution is not None else "N/A",
)
k7.metric(
    "SLA compliance",
    f"{sla:.1f}%" if sla is not None else "N/A",
)

# --------------------------------------------------
# 4. Trends and department comparisons
# --------------------------------------------------
st.subheader("Performance trends")

daily = (
    filtered.groupby("date", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        cost=("cost", "sum"),
    )
)

fig = px.line(
    daily,
    x="date",
    y=["revenue", "cost"],
    markers=True,
    title="Daily revenue vs. operating cost",
    labels={"value": "Amount ($)", "date": "Date", "variable": "Metric"},
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Department performance")

display_summary = dept_summary.copy()
display_summary["revenue"] = display_summary["revenue"].map(
    lambda x: f"${x:,.2f}"
)
display_summary["cost"] = display_summary["cost"].map(
    lambda x: f"${x:,.2f}"
)
display_summary["profit"] = display_summary["profit"].map(
    lambda x: f"${x:,.2f}"
)

st.dataframe(display_summary, use_container_width=True, hide_index=True)

# --------------------------------------------------
# 5. Generate AI report through LangGraph
# --------------------------------------------------
st.subheader("AI-generated management report")
st.write(
    "Generate an executive summary based on the calculated metrics "
    "and selected departments."
)

if st.button("Generate management report", type="primary"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "OPENAI_API_KEY is missing. Add it to your .env file "
            "and restart the app."
        )
    else:
        try:
            with st.spinner("Generating and validating the report..."):
                result = create_report(
                    metrics=metrics,
                    departments=dept_summary.to_dict(orient="records"),
                )
                st.session_state["report_result"] = result
                st.session_state["report_metrics"] = metrics
                st.session_state["report_departments"] = (
                    dept_summary.to_dict(orient="records")
                )
        except Exception as exc:
            st.error(
                "Report generation failed. Check your API key, model "
                "access, network connection, and application logs."
            )
            # Avoid exposing credentials or full provider responses.
            print(f"Report generation error: {type(exc).__name__}: {exc}")

result = st.session_state.get("report_result")

if result:
    report = result["report"]
    report_metrics = st.session_state.get("report_metrics", metrics)

    st.markdown("### Executive summary")
    st.write(report["executive_summary"])

    st.markdown("### Key findings")
    for finding in report["key_findings"]:
        st.markdown(f"- {finding}")

    st.markdown("### Recommendations")
    for recommendation in report["recommendations"]:
        st.markdown(f"- {recommendation}")

    st.markdown("### Risks and caveats")
    for caveat in report["risks_or_caveats"]:
        st.markdown(f"- {caveat}")

    st.caption(result["validation_message"])

    # Export a standalone Markdown report.
    lines = [
        "# Internal Operations Report",
        "",
        "## Reporting period",
        f"{report_metrics['period_start']} to {report_metrics['period_end']}",
        "",
        "## Executive summary",
        report["executive_summary"],
        "",
        "## Key findings",
    ]

    lines.extend(f"- {item}" for item in report["key_findings"])
    lines.extend(["", "## Recommendations"])
    lines.extend(f"- {item}" for item in report["recommendations"])
    lines.extend(["", "## Risks and caveats"])
    lines.extend(f"- {item}" for item in report["risks_or_caveats"])
    lines.extend([
        "",
        "> AI-generated content based on synthetic or uploaded data. "
        "Review before business use.",
    ])

    st.download_button(
        "Download management report (Markdown)",
        data="\n".join(lines),
        file_name="internal_operations_report.md",
        mime="text/markdown",
    )

st.download_button(
    "Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_operations.csv",
    mime="text/csv",
)