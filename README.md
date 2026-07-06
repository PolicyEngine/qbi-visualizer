# QBI Visualizer

An interactive calculator and visualizer for the Qualified Business Income Deduction (26 USC § 199A), built on [PolicyEngine US](https://github.com/PolicyEngine/policyengine-us).

The app has three tabs:

1. **QBID Calculator** — enter income sources, business properties, and filing status, and run a real PolicyEngine US simulation to compute the deduction.
2. **Law Structure** — a flowchart of § 199A showing how the statute maps to the calculation and to PolicyEngine code.
3. **Tax Forms** — how the calculation maps to IRS forms 8995 and 8995-A.

## Architecture

- **Frontend** (`frontend/`): Next.js (App Router) + TypeScript + Tailwind CSS 4, managed with [bun](https://bun.sh). Served under the base path `/us/qbi-calculator`. Deployed on Vercel.
- **Backend** (`backend/`): FastAPI + policyengine-us. Runs simulations server-side. Deployed on [Modal](https://modal.com).

The frontend calls `/api/*`, which `frontend/next.config.ts` rewrites to the backend: `http://localhost:8000` in development and the Modal deployment in production.

## Quick start

Prerequisites: Python 3.10–3.12, [bun](https://bun.sh).

Run `./start.sh` to set up and start both services, or start them manually:

**Terminal 1 — backend:**

```bash
cd backend
python3 -m venv venv          # first time only
venv/bin/pip install -e .     # first time only
venv/bin/uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend:**

```bash
cd frontend
bun install                   # first time only
bun run dev
```

Open http://localhost:3000/us/qbi-calculator.

## API endpoints

The backend serves interactive docs at http://localhost:8000/docs.

- `GET /` — app status
- `GET /health` — health check
- `GET /api/qbi/inputs` — input variables for the calculator
- `GET /api/qbi/outputs` — output variables the calculator returns
- `POST /api/qbi/calculate` — run a PolicyEngine US simulation for a household
- `GET /api/law/structure` — § 199A law structure data
- `GET /api/forms/mapping` — IRS form mapping data

## Project structure

```
qbi-visualizer/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, registers routers
│   │   ├── api/             # calculator, law_structure, tax_form_mapping routers
│   │   └── services/        # calculator.py runs PolicyEngine US simulations
│   └── modal_app.py         # Modal deployment wrapper
├── frontend/
│   ├── src/                 # Next.js App Router UI
│   └── next.config.ts       # basePath and /api proxy target
├── vercel.json              # Vercel build config (bun, frontend/)
└── DEPLOYMENT.md            # deployment guide
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for deploying the backend to Modal and the frontend to Vercel.

## Contributing

To contribute to the underlying QBI calculation, see [PolicyEngine/policyengine-us](https://github.com/PolicyEngine/policyengine-us).

## License

Not yet specified.
