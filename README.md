# AI-Powered Internal Reporting Assistant

A proof-of-concept Streamlit dashboard that transforms raw operational data into AI-assisted management reports in minutes.

## Problem Statement

Internal reporting requires repetitive data processing and manual summary writing. This prototype demonstrates how to automate the pipeline: ingest CSV data → calculate KPIs deterministically → generate executive summaries with an LLM → export ready-to-share reports.

## Solution Overview

- **Streamlit UI** — CSV upload, period/department filters, KPIs, charts, downloads
- **Pandas analytics layer** — Validation, aggregation, KPI calculations, period-over-period comparisons
- **LangGraph workflow** — Structured LLM call → schema validation → formatted report output

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   CSV Data  │────▶│  Pandas/Metrics  │────▶│   LangGraph LLM     │
│  (Upload or │     │  (Deterministic  │     │  (Generate +        │
│   Sample)   │     │   KPIs Only)     │     │   Validate Report)  │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                           │                         │
                           ▼                         ▼
                    ┌──────────────────┐     ┌─────────────────────┐
                    │  Streamlit UI    │     │  Markdown/CSV       │
                    │  (Charts, KPIs,  │     │  Export             │
                    │   Filters)       │     │                     │
                    └──────────────────┘     └─────────────────────┘
```

## Tech Stack

- **Python** 3.10+
- **Streamlit** — Dashboard framework
- **Pandas / NumPy** — Data processing
- **Plotly** — Interactive charts
- **LangChain + LangGraph** — LLM orchestration
- **OpenAI** — LLM provider (via `langchain-openai`)
- **Pydantic** — Structured output validation
- **python-dotenv** — Environment management

## Quick Start

### 1. Clone and create environment

```bash
git clone <your-repo-url>
cd ai-reporting-assistant

python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Generate sample data (one-time)

```bash
python -c "from reporting.data import generate_sample_data; generate_sample_data().to_csv('data/sample_operations.csv', index=False)"
```

### 5. Run the dashboard

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Usage

1. **Use sample data** — Loads synthetic 90-day operational data for Sales, Operations, and Customer Support
2. **Or upload CSV** — Must contain columns: `date`, `department`, `revenue`, `cost`, `tickets_opened`, `tickets_resolved`, `sla_met`
3. **Filter** — Select reporting period and departments
4. **View KPIs** — Revenue, cost, profit, margin, resolution rate, SLA compliance
5. **Generate report** — Click "Generate management report" to invoke the LangGraph workflow
6. **Download** — Export the AI report as Markdown or the filtered data as CSV

## Sample Output

### Dashboard KPIs
- Revenue, Operating Cost, Profit, Profit Margin
- Tickets Opened, Resolution Rate, SLA Compliance
- Daily revenue vs. cost trend chart
- Department-level performance table

### AI-Generated Report Sections
- **Executive Summary** — Concise management overview
- **Key Findings** — 3–5 evidence-based observations
- **Recommendations** — Practical next steps tied to data
- **Risks & Caveats** — Limitations, data-quality concerns, missing context

## Limitations

- **Synthetic data** — Numbers are illustrative, not real business results
- **CSV schema** — Fixed column requirements; no dynamic schema detection
- **LLM dependency** — Requires OpenAI API key and network access
- **Human review required** — AI-generated content must be validated before business use
- **No persistence** — No database, authentication, or scheduled execution
- **Single report type** — One workflow, one output format

## Future Improvements

- Scheduled/automated report generation
- Database connectors (PostgreSQL, Snowflake, BigQuery)
- Access controls and audit logging
- Delivery via email, Teams, or Slack
- Multi-period comparison and forecasting
- Custom report templates per stakeholder

## Project Structure

```
ai-reporting-assistant/
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore
├── README.md
├── data/
│   └── sample_operations.csv  # Generated sample data
└── reporting/
    ├── __init__.py
    ├── data.py                # Data generation & validation
    ├── metrics.py             # KPI calculations
    └── workflow.py            # LangGraph LLM workflow
```

## License

Prototype for demonstration purposes only.