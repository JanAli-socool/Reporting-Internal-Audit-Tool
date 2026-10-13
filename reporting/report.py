"""Render a generated report and its KPI snapshot as standalone Markdown."""

KPI_ROWS = [
    ("Revenue", "revenue", "money"),
    ("Operating cost", "cost", "money"),
    ("Profit", "profit", "money"),
    ("Profit margin", "profit_margin_pct", "pct"),
    ("Tickets opened", "tickets_opened", "count"),
    ("Tickets resolved", "tickets_resolved", "count"),
    ("Resolution rate", "resolution_rate_pct", "pct"),
    ("SLA compliance", "sla_compliance_pct", "pct"),
]


def format_value(value, kind: str) -> str:
    if value is None or value != value:  # None or NaN
        return "N/A"
    if kind == "money":
        return f"${value:,.2f}"
    if kind == "pct":
        return f"{value:.2f}%"
    return f"{value:,.0f}"


def format_change(entry: dict | None, kind: str) -> str:
    if not entry:
        return "—"
    change = entry["change"]
    if kind == "pct":
        return f"{change:+.2f} pp"
    pct = entry.get("change_pct")
    suffix = f" ({pct:+.2f}%)" if pct is not None else ""
    if kind == "money":
        sign = "-" if change < 0 else "+"
        return f"{sign}${abs(change):,.2f}{suffix}"
    return f"{change:+,.0f}{suffix}"


def build_report_markdown(snapshot: dict) -> str:
    """Build the export from the snapshot captured at generation time.

    Everything here comes from the snapshot rather than the live filters,
    so a downloaded report always matches the data its narrative used.
    """
    metrics = snapshot["metrics"]
    report = snapshot["result"]["report"]
    comparison = snapshot.get("comparison") or {}
    changes = comparison.get("changes", {}) if comparison.get("available") else {}

    lines = [
        "# PerfectSight — Internal Operations Report",
        "",
        f"**Reporting period:** {metrics['period_start']} to "
        f"{metrics['period_end']}  ",
        f"**Departments:** {', '.join(snapshot['selected_departments'])}  ",
        f"**Data source:** {snapshot['data_source']} "
        f"({metrics['record_count']:,} records)  ",
        f"**Generated:** {snapshot['generated_at']}",
    ]

    if comparison.get("available"):
        lines.append(
            f"**Compared with:** {comparison['previous_period_start']} to "
            f"{comparison['previous_period_end']}"
        )

    lines += [
        "",
        "## Key metrics",
        "",
        "Calculated deterministically with Python/Pandas.",
        "",
        "| Metric | Value | Change vs. previous period |",
        "| --- | ---: | ---: |",
    ]
    for label, key, kind in KPI_ROWS:
        lines.append(
            f"| {label} | {format_value(metrics.get(key), kind)} "
            f"| {format_change(changes.get(key), kind)} |"
        )

    lines += [
        "",
        "## Department performance",
        "",
        "| Department | Revenue | Cost | Profit | Margin | Resolution | SLA |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in snapshot["departments"]:
        lines.append(
            f"| {row['department']} "
            f"| {format_value(row['revenue'], 'money')} "
            f"| {format_value(row['cost'], 'money')} "
            f"| {format_value(row['profit'], 'money')} "
            f"| {format_value(row.get('profit_margin_pct'), 'pct')} "
            f"| {format_value(row.get('resolution_rate_pct'), 'pct')} "
            f"| {format_value(row.get('sla_compliance_pct'), 'pct')} |"
        )

    lines += ["", "## Executive summary", "", report["executive_summary"]]

    for title, key in [
        ("Key findings", "key_findings"),
        ("Recommendations", "recommendations"),
        ("Risks and caveats", "risks_or_caveats"),
    ]:
        lines += ["", f"## {title}", ""]
        lines.extend(f"- {item}" for item in report[key])

    warnings = snapshot["result"].get("warnings") or []
    if warnings:
        lines += ["", "## Review flags", ""]
        lines.extend(f"- {w}" for w in warnings)

    lines += [
        "",
        "---",
        "",
        "> AI-generated narrative based on "
        f"{snapshot['data_source'].lower()}. KPIs are calculated in Python; "
        "the narrative must be reviewed by a person before business use.",
        "",
    ]
    return "\n".join(lines)
