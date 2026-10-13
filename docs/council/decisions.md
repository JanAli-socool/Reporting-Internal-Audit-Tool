## P1
**Decision:** Reorder the page to Overview (KPIs) → action bar ("Generate management report") → report card → Evidence (trends, departments). One scroll, no tabs. Retitle the section "Management report (AI draft)". *Unanimous; tabs rejected per 06.*

## P2
**Decision:** Add `.streamlit/config.toml` with `primaryColor = "#2a78d6"` (validated slot 1), and use neutral pills. Red and green are reserved for deltas and status. The wordmark uses the same primary.

## P3
**Decision:** Keep the delta color rule (good = green, bad = red, volume = grey) and document it in code. The UI uses "pts", the export keeps "percentage points". State the window once: "Compared with the previous 30 days (16 Aug – 14 Sep)".

## P4
**Decision:** Replace the 7-day line with weekly grouped bars, current vs. previous period, with "previous" in a muted step of the same hue. Do not tune the generator (10). Fallback if time runs out: the caption from 11. *Highest priority after P1.*

## P5
**Decision:** The backend returns `figures_checked` / `figures_matched`. The report card opens with a checklist row: "✓ All 4 sections present · ✓ N of N figures match the calculated data · ⚠ k to verify", using icon + label + status color. Each warning names the figure and the action.

## P6
**Decision:** Cheap wins only: the table defaults to five columns, with the rest in an expander. Moving the report up (P1) is the main mobile gain. Breakpoint-specific tile layouts are deferred (09 overrules 08 on cost). Record the demo at 1440px.

## P7
**Decision:** A type-only wordmark ("Perfect" ink + "Sight" primary) and one tagline: "From raw operational data to a reviewed management report in minutes." No glyph, and no implication that this is an official client product, until the name is confirmed.

## P8
**Decision:** Replace `st.spinner` with `st.status`, driven by real `workflow.stream()` node events. Steps: "Preparing verified metrics" → "Writing the narrative" → "Checking structure and figures".

## Implementation order (about one day)
1. P1 reorder · 2. P2 theme · 3. P5 checklist + counts · 4. P4 weekly comparison chart · 5. P8 status steps · 6. P3/P7 copy · 7. P6 table columns.

**Deferred:** a responsive tile layout, a logo glyph, tabs.
