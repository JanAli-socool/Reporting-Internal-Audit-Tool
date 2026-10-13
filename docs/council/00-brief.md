# Council brief

**Subject:** PerfectSight AI Reporting Assistant (`app.py`, `docs/dashboard.png`)
**Audience:** a two-minute recorded demo for a hiring manager, then extension by the developer.

## Protocol (file-based coordination only)

1. The chair writes this brief. Problems are fixed as P1–P8 below.
2. Each member writes exactly one file, `members/NN-role.md`, with one `## Pn` section per problem they take a position on.
3. Members write in numeric order and **must read every earlier member file first**. To agree or disagree, cite the file, e.g. `(re: 03-product-designer.md)`. There is no chat and no IPC; the files are the only channel.
4. Positions are one to three sentences and opinionated. Members omit problems outside their remit instead of padding.
5. The chair writes `decisions.md` from the member files. `assemble.py` compiles everything into `../design-council.md`.

## Problems

- **P1 — Report placement:** the AI report, the point of the demo, sits about 1,500px down, below the charts.
- **P2 — Color:** the default Streamlit red on buttons and pills clashes with the red/green delta semantics.
- **P3 — Deltas and copy:** "pp", the inverse/neutral delta colors, and the comparison caption wording.
- **P4 — Revenue chart:** the 7-day line slopes down while the KPI says +2.9%, which looks like a contradiction.
- **P5 — AI trust cues:** figure grounding, the main differentiator, appears only as a small caption.
- **P6 — Narrow screens:** 8 KPI tiles, a 9-column table, and filters hidden in the sidebar.
- **P7 — Identity:** an emoji favicon, a two-part caption, and no wordmark.
- **P8 — Generation latency:** a bare spinner for a 5–15 s LLM call.
