# Two-minute demo script

**Before recording:** `.env` has a working key, the app is running
(`streamlit run app.py`), the browser is zoomed to about 90%, and the sidebar
is open. Generate one report beforehand to warm up the API, then refresh the
page.

| Time | On screen | Say |
| --- | --- | --- |
| 0:00 | Dashboard header | "This proof of concept shows how internal operational data can become a management-ready report with much less manual effort. Everything here is synthetic data." |
| 0:20 | KPI tiles | "It defaults to the last 30 days and compares against the previous 30. Every number is calculated in Python with Pandas, not by the AI. Revenue and profit are up, but SLA compliance has dropped 3.6 points." |
| 0:35 | SLA chart, then deselect *Sales* in the sidebar | "The trend shows where: Operations SLA fell sharply in late September. Filters recalculate everything instantly." Re-select *Sales*. |
| 0:50 | Click **Generate management report** | "Now a LangGraph workflow sends only those verified metrics to the LLM. It writes the narrative, and a validation step checks the structure and that every figure it quotes matches the calculated data." |
| 1:25 | Scroll through the report and its validation message | "Executive summary, findings, recommendations, and caveats. If the model quoted a number that isn't in the data, it would be flagged here for review." |
| 1:35 | Change a filter to show the stale warning, then click **Download management report** | "The report is tied to the data it was generated from. Change the filters and it's marked as out of date. The export includes the KPI tables and the narrative." |
| 1:45 | Back to the top | "This is a starting point. The next step would be to confirm the real reporting requirements, connect the actual data sources, and agree the report format and delivery schedule." |

**Fallbacks:** if the API is slow during recording, cut the wait in editing.
If generation fails, the app shows a clean error and the dashboard keeps
working. Re-record that segment.
