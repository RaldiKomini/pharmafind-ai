# PharmaFind AI — Frontend

Polished React + TypeScript + Vite + Tailwind frontend for the PharmaFind AI pharmacovigilance backend.

## Prerequisites

- Backend running locally at `http://127.0.0.1:8000`
- Node.js 18+

## Install & run

```bash
cd frontend
npm install   # or: bun install / pnpm install
npm run dev
```

Then open http://localhost:5173.

## Scripts

- `npm run dev` — start Vite dev server (proxies `/api` → `http://127.0.0.1:8000`)
- `npm run build` — type-check + production build
- `npm run preview` — preview the built app

## Config

Override the backend URL with an env var if needed:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

By default, the frontend calls `/api/...` and Vite proxies (and rewrites away `/api`) to the backend, so no CORS configuration is required on the backend.

## Notes

- This UI is a **signal-review assistant** — not a diagnostic or medical recommendation tool.
- FAERS reports do not establish causality. Report counts are not incidence rates.
