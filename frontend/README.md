# PharmaFind AI Frontend

React + TypeScript + Vite + Tailwind dashboard for PRR/ROR FAERS signal review, PubMed evidence retrieval, agent workflows, and PDF export.

## Prerequisites

- Backend running at `http://127.0.0.1:8000`
- Node.js 20.19+ or 22.12+

## Install and Run

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Screenshots

- [Deterministic review](../docs/screenshots/deterministic-review.png)
- [Agent workflow](../docs/screenshots/agent-workflow.png)

## Scripts

- `npm run dev` - start Vite with the local `/api` proxy.
- `npm run build` - type-check and create a production build.
- `npm run preview` - preview the production build.

Set `VITE_API_BASE_URL` to override the default `/api` base URL.

## UI Behavior

- Deterministic mode runs the PRR/ROR + PubMed review through `/api/reviews`.
- Agent mode calls backend tools for reviews, comparisons, signal explanations, and cached PDF export.
- The Download PDF button sends the already-rendered Markdown report to `/api/reviews/pdf`; it does not rerun FAERS or PubMed.
- PDF files are generated server-side with ReportLab.

The interface is a signal-review assistant, not a diagnostic or medical recommendation tool. FAERS reports do not establish causality; PRR and ROR measure reporting disproportionality, not incidence.
