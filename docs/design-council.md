# PerfectSight Design Council — Deliberation

Compiled by `docs/council/assemble.py` from the files in `docs/council/`. Members coordinated only through those files (see `00-brief.md` for the protocol). Edit the sources, not this file.

**Members:** Principal UX Researcher, Staff Web Designer, Staff Product Designer, Design Systems Lead, Visual Design Director, Information Architect, Human Factors Specialist, Mobile UX Specialist, Staff Frontend Developer, Staff Backend Developer, Content Writer, Senior Logo Designer

## P1: Report placement

- **Principal UX Researcher** (`01-ux-researcher.md`): The demo asks "report in minutes?" but opens like a generic BI page. Viewers decide in the first 20 seconds; the report must appear above the fold.
- **Staff Web Designer** (`02-web-designer.md`): Agree with 01-ux-researcher.md. Put the CTA in the overview band and the report card directly beneath it.
- **Staff Product Designer** (`03-product-designer.md`): Reorder the page to Overview → Report → Evidence. The charts support the report; they aren't the product.
- **Design Systems Lead** (`04-design-systems.md`): No new components needed: an existing `st.container(border=True)` moved up the page.
- **Visual Design Director** (`05-visual-design.md`): Agree with 03-product-designer.md. The page's visual weight should peak at the report card, not the line charts.
- **Information Architect** (`06-information-architect.md`): Order the page by the question it answers: *What happened?* (KPIs) → *What does it mean?* (report) → *Show me* (evidence). Not tabs: a recording needs a single scroll.
- **Human Factors Specialist** (`07-human-factors.md`): Keep the button close to where its result appears. A sidebar CTA with the result 1,000px away causes "did anything happen?" moments (re: 02-web-designer.md, which agrees).
- **Mobile UX Specialist** (`08-mobile-ux.md`): On mobile the report is currently about 4,000px down. Moving it up (re: 06-information-architect.md) is the single biggest mobile improvement, and it costs nothing.
- **Staff Frontend Developer** (`09-frontend-dev.md`): Move the section; about an hour of work. The session-state snapshot logic doesn't change.
- **Content Writer** (`11-content-writer.md`): Retitle the section "Management report (AI draft)". "AI-generated" in the heading undersells the review step.

**Decision:** Reorder the page to Overview (KPIs) → action bar ("Generate management report") → report card → Evidence (trends, departments). One scroll, no tabs. Retitle the section "Management report (AI draft)". *Unanimous; tabs rejected per 06.*

## P2: Color

- **Principal UX Researcher** (`01-ux-researcher.md`): Red controls next to red deltas create false alarms in a recording. Fix it.
- **Staff Web Designer** (`02-web-designer.md`): Neutral pills (department identity already lives in the chart colors) and a blue primary button.
- **Staff Product Designer** (`03-product-designer.md`): The primary action must not be status red. Exact values go to the visual and systems leads.
- **Design Systems Lead** (`04-design-systems.md`): Define one theme in `.streamlit/config.toml`: `primaryColor = "#2a78d6"` (categorical slot 1, already validated). Red and green are reserved for status.
- **Visual Design Director** (`05-visual-design.md`): Red is on every control today, so the eye can't find what is actually bad. Use the blue primary from 04-design-systems.md, with neutral-grey pills.
- **Human Factors Specialist** (`07-human-factors.md`): Red-on-red is a signal-detection problem: when everything is salient, nothing is.
- **Staff Frontend Developer** (`09-frontend-dev.md`): One config file (re: 04-design-systems.md). Multiselect pill color follows `primaryColor` automatically.
- **Senior Logo Designer** (`12-logo-designer.md`): The wordmark blue must be the same primary as the UI (re: 04-design-systems.md), not a separate brand blue.

**Decision:** Add `.streamlit/config.toml` with `primaryColor = "#2a78d6"` (validated slot 1), and use neutral pills. Red and green are reserved for deltas and status. The wordmark uses the same primary.

## P3: Deltas and copy

- **Principal UX Researcher** (`01-ux-researcher.md`): Non-analysts don't read "pp". Grey for ticket volume is correct: more tickets is neither good nor bad.
- **Staff Web Designer** (`02-web-designer.md`): Keep the tiles. Tighten the caption to one line: "vs. previous 30 days · 16 Aug – 14 Sep".
- **Staff Product Designer** (`03-product-designer.md`): Say "pts" in the UI and keep "percentage points" in the Markdown export, where precision matters.
- **Design Systems Lead** (`04-design-systems.md`): Delta colors follow one rule: good direction = green, bad = red, volume = grey. Document the rule in code next to the tiles.
- **Visual Design Director** (`05-visual-design.md`): No change to the delta colors; the existing logic is sound (re: 04-design-systems.md).
- **Information Architect** (`06-information-architect.md`): State the comparison window once, at the top, not in each tile.
- **Human Factors Specialist** (`07-human-factors.md`): Treating cost as an inverse metric is correct but invisible: "Cost ↑ (red)" works only because the tile says "Operating cost". Keep the labels explicit.
- **Staff Frontend Developer** (`09-frontend-dev.md`): Change the `pp_delta` format string to "pts". Trivial.
- **Content Writer** (`11-content-writer.md`): Use "pts" (agree with 03-product-designer.md). Caption: "Compared with the previous 30 days (16 Aug – 14 Sep)".

**Decision:** Keep the delta color rule (good = green, bad = red, volume = grey) and document it in code. The UI uses "pts", the export keeps "percentage points". State the window once: "Compared with the previous 30 days (16 Aug – 14 Sep)".

## P4: Revenue chart

- **Principal UX Researcher** (`01-ux-researcher.md`): The highest-risk item. An interviewer who spots a "contradiction" stops trusting every number. It must be resolved, not just captioned.
- **Staff Web Designer** (`02-web-designer.md`): Two charts that look alike and disagree are worse than one. Replace the line rather than annotating it.
- **Staff Product Designer** (`03-product-designer.md`): Show current vs. previous period weekly. It tells the same story as the KPI tiles, so the demo's narrative holds.
- **Design Systems Lead** (`04-design-systems.md`): Reuse the three validated slots. "Previous period" uses a muted step of the same hue, never a fourth color.
- **Visual Design Director** (`05-visual-design.md`): Weekly grouped bars, current vs. previous. The +2.9% becomes visible instead of contradicted.
- **Information Architect** (`06-information-architect.md`): The line answers "shape within the window" and the KPI answers "window total". Two questions on one page with no label is an IA bug. Agree with 05-visual-design.md: replace the line.
- **Mobile UX Specialist** (`08-mobile-ux.md`): Weekly bars also read better than daily lines at 360px.
- **Staff Frontend Developer** (`09-frontend-dev.md`): `daily_trend` → weekly resample, plus the previous window from `period_comparison`'s bounds. About two hours including tests.
- **Staff Backend Developer** (`10-backend-dev.md`): The data is correct; it's seeded noise. Don't "fix" it by tuning the generator to look nicer; that's manufacturing a story. Change the chart (agree with 05-visual-design.md).
- **Content Writer** (`11-content-writer.md`): If the chart can't change today, add the caption "Shape within the selected period. See the KPIs for period totals."

**Decision:** Replace the 7-day line with weekly grouped bars, current vs. previous period, with "previous" in a muted step of the same hue. Do not tune the generator (10). Fallback if time runs out: the caption from 11. *Highest priority after P1.*

## P5: AI trust cues

- **Principal UX Researcher** (`01-ux-researcher.md`): Trust is the thesis. Make the check visible and countable: "14 of 14 figures matched".
- **Staff Web Designer** (`02-web-designer.md`): A checklist row at the top of the report card, not a toast at the bottom.
- **Staff Product Designer** (`03-product-designer.md`): This is the feature to sell. Every unverified figure gets a clear next step ("Verify 17.4% before sharing").
- **Design Systems Lead** (`04-design-systems.md`): Use the status palette (success/warning) with an icon and a label, never color alone.
- **Visual Design Director** (`05-visual-design.md`): A single row of three check icons, set at body text size, not caption size.
- **Information Architect** (`06-information-architect.md`): Validation results belong inside the report card, because they describe that artifact.
- **Human Factors Specialist** (`07-human-factors.md`): Warnings must be actionable and specific, not generic yellow banners (re: 03-product-designer.md).
- **Staff Frontend Developer** (`09-frontend-dev.md`): Needs counts from the backend (see 10-backend-dev.md); rendering is trivial.
- **Staff Backend Developer** (`10-backend-dev.md`): `validate_report` already parses every figure. Return `figures_checked` and `figures_matched` alongside the warnings. Small change, and covered by the existing workflow tests.
- **Content Writer** (`11-content-writer.md`): "✓ All 4 sections present · ✓ 14 of 14 figures match the calculated data · ⚠ 1 figure to verify". Concrete counts, no adjectives.

**Decision:** The backend returns `figures_checked` / `figures_matched`. The report card opens with a checklist row: "✓ All 4 sections present · ✓ N of N figures match the calculated data · ⚠ k to verify", using icon + label + status color. Each warning names the figure and the action.

## P6: Narrow screens

- **Principal UX Researcher** (`01-ux-researcher.md`): The audience watches a laptop recording. Mobile is a non-goal for this milestone.
- **Staff Web Designer** (`02-web-designer.md`): Streamlit columns stack well enough. Cut the table to five columns and put the rest in an expander.
- **Staff Product Designer** (`03-product-designer.md`): Agree with 01-ux-researcher.md: non-goal. The README's limitations section already covers scope.
- **Information Architect** (`06-information-architect.md`): Fewer columns by default (agree with 02-web-designer.md). Revenue share and ticket counts go in the expander.
- **Mobile UX Specialist** (`08-mobile-ux.md`): I disagree with treating it as a full non-goal (re: 01-ux-researcher.md, 03-product-designer.md). Fix the cheap things now: five table columns, and KPI tiles that stack as 2×4 rather than 4×2 on narrow screens. Defer the real responsive work. Filters hidden in the sidebar are acceptable for a prototype.
- **Staff Frontend Developer** (`09-frontend-dev.md`): Streamlit can't switch 2×4 vs. 4×2 by breakpoint without CSS hacks (re: 08-mobile-ux.md). I'll do the table columns only.

**Decision:** Cheap wins only: the table defaults to five columns, with the rest in an expander. Moving the report up (P1) is the main mobile gain. Breakpoint-specific tile layouts are deferred (09 overrules 08 on cost). Record the demo at 1440px.

## P7: Identity

- **Principal UX Researcher** (`01-ux-researcher.md`): Low priority. Nobody judges a prototype by its logo, but an emoji favicon does read as "template".
- **Staff Web Designer** (`02-web-designer.md`): A text wordmark in the header is enough. No image assets.
- **Staff Product Designer** (`03-product-designer.md`): Don't over-brand a prototype for someone else's company; "PerfectSight" may be the client's name. Confirm before investing.
- **Design Systems Lead** (`04-design-systems.md`): The wordmark uses theme tokens (ink + primary), so it changes with the theme automatically.
- **Visual Design Director** (`05-visual-design.md`): Restraint: the wordmark is "Perfect" in ink and "Sight" in primary. No glyph until the client confirms the name (re: 03-product-designer.md).
- **Staff Frontend Developer** (`09-frontend-dev.md`): A Markdown header with an inline `<span>` for the wordmark. No assets.
- **Content Writer** (`11-content-writer.md`): One tagline, not two: "From raw operational data to a reviewed management report in minutes."
- **Senior Logo Designer** (`12-logo-designer.md`): An emoji favicon says "template". A minimal mark (an aperture formed from two arcs) would carry "Sight" and stay legible at 16px. But I agree with 03-product-designer.md and 05-visual-design.md: don't design a mark for a name the client may own. Ship the type-only wordmark now and the glyph after the name is confirmed. Never imply this is an official client product.

**Decision:** A type-only wordmark ("Perfect" ink + "Sight" primary) and one tagline: "From raw operational data to a reviewed management report in minutes." No glyph, and no implication that this is an official client product, until the name is confirmed.

## P8: Generation latency

- **Principal UX Researcher** (`01-ux-researcher.md`): A silent 10-second wait is where demos lose people. Show progress.
- **Staff Web Designer** (`02-web-designer.md`): `st.status` with three steps (agree with 01-ux-researcher.md).
- **Staff Product Designer** (`03-product-designer.md`): Name the progress steps after the graph nodes, so the progress UI doubles as the architecture explanation.
- **Design Systems Lead** (`04-design-systems.md`): `st.status` is native and needs no custom CSS.
- **Human Factors Specialist** (`07-human-factors.md`): A spinner is fine under about 10 s. Above that, people need step-by-step progress. The p95 here is about 15 s, so use steps.
- **Staff Frontend Developer** (`09-frontend-dev.md`): `st.status`, with the graph run via `stream()` so each node completion updates the status. No fake steps.
- **Staff Backend Developer** (`10-backend-dev.md`): One structured call, a 60 s timeout, and one retry: typically 5–15 s with gpt-4o-mini. Using `workflow.stream()` for real node events (re: 09-frontend-dev.md) is supported in LangGraph 1.2.
- **Content Writer** (`11-content-writer.md`): Step labels: "Preparing verified metrics", "Writing the narrative", "Checking structure and figures".

**Decision:** Replace `st.spinner` with `st.status`, driven by real `workflow.stream()` node events. Steps: "Preparing verified metrics" → "Writing the narrative" → "Checking structure and figures".

## Implementation order (about one day)
1. P1 reorder · 2. P2 theme · 3. P5 checklist + counts · 4. P4 weekly comparison chart · 5. P8 status steps · 6. P3/P7 copy · 7. P6 table columns.

**Deferred:** a responsive tile layout, a logo glyph, tabs.
