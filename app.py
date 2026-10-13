import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from reporting.data import REQUIRED_COLUMNS, generate_sample_data, validate_data
from reporting.metrics import (
    calculate_metrics,
    daily_trend,
    department_summary,
    filter_records,
    period_comparison,
)
from reporting.report import build_report_markdown
from reporting.workflow import create_report

load_dotenv()

APP_DIR = Path(__file__).parent

# Reference categorical palette, slots 1-3 (validated for all pairs).
# Colors follow the entity, so filtering never repaints a series.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
METRIC_COLORS = {"Revenue": SERIES[0], "Operating cost": SERIES[1]}

st.set_page_config(
    page_title="PerfectSight · AI Reporting Assistant",
    page_icon="📊",
    layout="wide",
)

st.title("PerfectSight — AI Reporting Assistant")
st.caption(
    "Business Analytics, EPM & Data Management · Turn raw operational data "
    "into a reviewed management report in minutes"
)

# --------------------------------------------------
# 1. Load sample data or upload a CSV
# --------------------------------------------------
@st.cache_data
def load_demo_data():
    sample_path = APP_DIR / "data" / "sample_operations.csv"
    if sample_path.exists():
        return validate_data(pd.read_csv(sample_path))
    return validate_data(generate_sample_data())


@st.cache_data
def load_uploaded_data(content: bytes):
    from io import BytesIO

    return validate_data(pd.read_csv(BytesIO(content)))


with st.sidebar:
    st.header("Report configuration")
    uploaded_file = st.file_uploader(
        "Upload operational data",
        type=["csv"],
        help="Required columns: " + ", ".join(REQUIRED_COLUMNS),
    )

    st.caption(
        "Demo data is synthetic. Do not upload confidential "
        "company data to this prototype."
    )

try:
    if uploaded_file is not None:
        df = load_uploaded_data(uploaded_file.getvalue())
        data_source = f"Uploaded CSV ({uploaded_file.name})"
    else:
        df = load_demo_data()
        data_source = "Synthetic demo data"
except pd.errors.EmptyDataError:
    st.error("Could not load the dataset: the file is empty.")
    st.stop()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.info(
        "Expected columns: " + ", ".join(f"`{c}`" for c in REQUIRED_COLUMNS)
    )
    st.stop()

dropped = df.attrs.get("dropped_rows", 0)
st.caption(f"Data source: {data_source} · {len(df):,} valid records")
if dropped:
    st.warning(
        f"{dropped:,} row(s) were excluded because of missing or invalid "
        "dates, departments, or numeric values."
    )

# --------------------------------------------------
# 2. Filters
# --------------------------------------------------
min_date = df["date"].min().date()
max_date = df["date"].max().date()
default_start = max(min_date, max_date - timedelta(days=29))

with st.sidebar:
    selected_dates = st.date_input(
        "Reporting period",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Defaults to the latest 30 days so the previous 30 days "
             "can be used for comparison.",
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

if not selected_departments:
    st.warning("Select at least one department.")
    st.stop()

filtered = filter_records(df, start_date, end_date, selected_departments)

if filtered.empty:
    st.warning("No records match these filters. Adjust your selections.")
    st.stop()

department_colors = {
    dept: SERIES[i % len(SERIES)] for i, dept in enumerate(departments)
}

# --------------------------------------------------
# 3. Deterministic KPIs
# --------------------------------------------------
metrics = calculate_metrics(filtered)
dept_summary = department_summary(filtered)
comparison = period_comparison(
    df, start_date, end_date, selected_departments
)
changes = comparison["changes"]

st.subheader("Executive overview")
if comparison["available"]:
    st.caption(
        f"{start_date:%d %b %Y} – {end_date:%d %b %Y} · changes vs. "
        f"{comparison['previous_period_start']} to "
        f"{comparison['previous_period_end']}"
    )
else:
    st.caption(
        f"{start_date:%d %b %Y} – {end_date:%d %b %Y} · no comparison: the "
        "data does not cover a full previous period of the same length"
    )


def money_delta(key):
    entry = changes.get(key)
    if not entry:
        return None
    pct = entry.get("change_pct")
    sign = "-" if entry["change"] < 0 else "+"
    text = f"{sign}${abs(entry['change']):,.0f}"
    return f"{text} ({pct:+.1f}%)" if pct is not None else text


def pp_delta(key):
    entry = changes.get(key)
    return f"{entry['change']:+.1f} pp" if entry else None


def count_delta(key):
    entry = changes.get(key)
    if not entry:
        return None
    pct = entry.get("change_pct")
    return f"{entry['change']:+,.0f}" + (f" ({pct:+.1f}%)" if pct is not None else "")


def pct_value(value):
    return f"{value:.1f}%" if value is not None else "N/A"


k1, k2, k3, k4 = st.columns(4)
k1.metric("Revenue", f"${metrics['revenue']:,.0f}", money_delta("revenue"))
k2.metric(
    "Operating cost",
    f"${metrics['cost']:,.0f}",
    money_delta("cost"),
    delta_color="inverse",
)
k3.metric("Profit", f"${metrics['profit']:,.0f}", money_delta("profit"))
k4.metric(
    "Profit margin",
    pct_value(metrics["profit_margin_pct"]),
    pp_delta("profit_margin_pct"),
)

k5, k6, k7, k8 = st.columns(4)
k5.metric(
    "Tickets opened",
    f"{metrics['tickets_opened']:,}",
    count_delta("tickets_opened"),
    delta_color="off",
)
k6.metric(
    "Tickets resolved",
    f"{metrics['tickets_resolved']:,}",
    count_delta("tickets_resolved"),
    delta_color="off",
)
k7.metric(
    "Resolution rate",
    pct_value(metrics["resolution_rate_pct"]),
    pp_delta("resolution_rate_pct"),
)
k8.metric(
    "SLA compliance",
    pct_value(metrics["sla_compliance_pct"]),
    pp_delta("sla_compliance_pct"),
)

# --------------------------------------------------
# 4. Trends and department comparisons
# --------------------------------------------------
st.subheader("Performance trends")


def style_chart(fig, y_title):
    fig.update_traces(line={"width": 2})
    fig.update_layout(
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.15, "x": 0, "title": None},
        margin={"l": 10, "r": 10, "t": 60, "b": 10},
        yaxis_title=y_title,
        xaxis_title=None,
    )
    fig.update_xaxes(showgrid=False)
    return fig


daily = daily_trend(filtered).set_index("date")
smoothed = (
    daily[["revenue", "cost"]]
    .rolling(7, min_periods=1)
    .mean()
    .rename(columns={"revenue": "Revenue", "cost": "Operating cost"})
    .reset_index()
)

c1, c2 = st.columns(2)

with c1:
    fig = px.line(
        smoothed,
        x="date",
        y=["Revenue", "Operating cost"],
        title="Daily revenue vs. operating cost (7-day average)",
        color_discrete_map=METRIC_COLORS,
    )
    fig.update_traces(hovertemplate="$%{y:,.0f}")
    st.plotly_chart(style_chart(fig, "Amount ($)"), width="stretch")

with c2:
    sla_daily = (
        filtered.groupby(["date", "department"], as_index=False)[
            ["sla_met", "tickets_resolved"]
        ].sum()
        .sort_values("date")
    )
    rolled = (
        sla_daily.groupby("department")[["sla_met", "tickets_resolved"]]
        .rolling(7, min_periods=1)
        .sum()
        .reset_index(level=0)
    )
    sla_daily["sla_compliance_pct"] = (
        rolled["sla_met"]
        / rolled["tickets_resolved"].replace(0, float("nan"))
        * 100
    )

    fig = px.line(
        sla_daily,
        x="date",
        y="sla_compliance_pct",
        color="department",
        title="SLA compliance by department (7-day rolling)",
        color_discrete_map=department_colors,
    )
    fig.update_traces(hovertemplate="%{y:.1f}%")
    st.plotly_chart(style_chart(fig, "SLA compliance (%)"), width="stretch")

st.subheader("Department performance")

def department_bar(column, title, axis_title, label_format):
    bars = dept_summary.sort_values("revenue")
    fig = px.bar(
        bars,
        x=column,
        y="department",
        orientation="h",
        color="department",
        color_discrete_map=department_colors,
        title=title,
        text=bars[column].map(label_format),
    )
    fig.update_traces(
        hovertemplate="%{y}: %{text}<extra></extra>",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_layout(
        height=260,
        showlegend=False,
        bargap=0.45,
        margin={"l": 10, "r": 40, "t": 50, "b": 10},
        xaxis_title=axis_title,
        yaxis_title=None,
    )
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=False)
    return fig


c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(
        department_bar(
            "profit", "Profit by department", "Profit ($)",
            lambda v: f"${v:,.0f}",
        ),
        width="stretch",
    )
with c4:
    st.plotly_chart(
        department_bar(
            "profit_margin_pct", "Profit margin by department", "Margin (%)",
            lambda v: f"{v:.1f}%",
        ),
        width="stretch",
    )

st.dataframe(
    dept_summary[[
        "department", "revenue", "cost", "profit", "profit_margin_pct",
        "revenue_share_pct", "tickets_opened", "resolution_rate_pct",
        "sla_compliance_pct",
    ]],
    width="stretch",
    hide_index=True,
    column_config={
        "department": "Department",
        "revenue": st.column_config.NumberColumn("Revenue", format="dollar"),
        "cost": st.column_config.NumberColumn("Cost", format="dollar"),
        "profit": st.column_config.NumberColumn("Profit", format="dollar"),
        "profit_margin_pct": st.column_config.NumberColumn(
            "Margin", format="%.1f%%"
        ),
        "revenue_share_pct": st.column_config.NumberColumn(
            "Revenue share", format="%.1f%%"
        ),
        "tickets_opened": st.column_config.NumberColumn(
            "Tickets", format="localized"
        ),
        "resolution_rate_pct": st.column_config.NumberColumn(
            "Resolution", format="%.1f%%"
        ),
        "sla_compliance_pct": st.column_config.NumberColumn(
            "SLA", format="%.1f%%"
        ),
    },
)

# --------------------------------------------------
# 5. Generate AI report through LangGraph
# --------------------------------------------------
st.subheader("AI-generated management report")
st.write(
    "Python calculates every figure above. The LangGraph workflow sends "
    "those verified figures to the LLM, which writes the narrative, then "
    "checks the output's structure and that its numbers match the metrics."
)

dept_records = dept_summary.to_dict(orient="records")
current_filters = {
    "data_source": data_source,
    "start": str(start_date),
    "end": str(end_date),
    "departments": list(selected_departments),
}

if st.button("Generate management report", type="primary"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error(
            "OPENAI_API_KEY is missing. Copy `.env.example` to `.env`, add "
            "your key, and restart the app. The dashboard above works "
            "without it."
        )
    else:
        try:
            with st.spinner("Generating and validating the report..."):
                result = create_report(
                    metrics=metrics,
                    departments=dept_records,
                    comparison=comparison,
                    data_source=data_source,
                )
            # Snapshot everything the report was based on, so later filter
            # changes cannot leak into what is displayed or exported.
            st.session_state["report_snapshot"] = {
                "result": result,
                "metrics": metrics,
                "departments": dept_records,
                "comparison": comparison,
                "filters": current_filters,
                "selected_departments": list(selected_departments),
                "data_source": data_source,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        except Exception as exc:
            st.error(
                "Report generation failed. Check your API key, model "
                "access, and network connection, then try again. The "
                "dashboard data is unaffected."
            )
            # Log the type and message only; never echo credentials.
            print(f"Report generation error: {type(exc).__name__}: {exc}")

snapshot = st.session_state.get("report_snapshot")

if snapshot:
    report = snapshot["result"]["report"]
    snap_metrics = snapshot["metrics"]

    if snapshot["filters"] != current_filters:
        st.warning(
            "Filters have changed since this report was generated. The "
            "report below (and its download) still reflects the original "
            "selection. Generate again to update it."
        )

    with st.container(border=True):
        st.caption(
            f"Report period: {snap_metrics['period_start']} to "
            f"{snap_metrics['period_end']} · Departments: "
            f"{', '.join(snapshot['selected_departments'])} · "
            f"Generated {snapshot['generated_at']}"
        )

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

        st.success(snapshot["result"]["validation_message"])
        for warning in snapshot["result"].get("warnings", []):
            st.warning(warning)

        st.caption(
            "AI-generated narrative. Review before business use."
        )

    st.download_button(
        "Download management report (Markdown)",
        data=build_report_markdown(snapshot),
        file_name=(
            f"perfectsight_report_{snap_metrics['period_start']}_"
            f"{snap_metrics['period_end']}.md"
        ),
        mime="text/markdown",
    )

st.download_button(
    "Download filtered data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name=f"filtered_operations_{start_date}_{end_date}.csv",
    mime="text/csv",
)
