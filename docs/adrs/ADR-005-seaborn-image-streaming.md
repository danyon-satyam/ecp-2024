# ADR-005: Seaborn Charts Streamed as PNG Images via API

**Date:** 2026-04-12
**Status:** Accepted
**Author:** Danyon Satyam
**Reviewed by:** Pramit Dash

---

## Context

Pramit's requirements include "meaningful visualisations using Seaborn."
The question was how to expose these visualisations through a REST API.

Two approaches were considered:

**Option A — Return raw data, let the client chart it**
API returns JSON aggregates. The client (React, dashboard tool) uses
its own charting library to render charts.

- Benefit: Flexible — client controls chart appearance
- Drawback: Every client must implement their own charting logic
- Drawback: Non-technical university staff cannot use it directly

**Option B — Generate charts server-side, stream as PNG**
API generates Seaborn charts in-memory and returns PNG images.

- Benefit: Non-technical users open a URL and see a chart instantly
- Benefit: Consistent chart appearance across all clients
- Benefit: Charts are embeddable anywhere (img src, email, PDF)
- Drawback: Less flexible for clients wanting custom styling

---

## Decision

We chose **Option B** — server-side Seaborn chart generation
streamed as PNG via `StreamingResponse`.

---

## Implementation Details

- `matplotlib.use("Agg")` forces non-interactive backend — critical
  for server environments with no display
- Charts are generated in `BytesIO` buffers — no disk I/O
- `plt.close(fig)` called after every chart to prevent memory leaks
- `StreamingResponse` with `media_type="image/png"` allows browsers
  to display charts directly by opening the endpoint URL
- All charts use consistent colour coding: Green=Positive,
  Blue=Neutral, Red=Negative for visual coherence

---

## Consequences

- Chart styling is centralised — changing colours or fonts is one edit
- Memory usage scales with concurrent chart requests (each holds a
  BytesIO buffer in RAM during streaming)
- For GCP deployment, Cloud Run's per-request memory limit must
  accommodate chart generation (~50MB per large chart)
