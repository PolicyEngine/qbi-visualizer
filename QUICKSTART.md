# Quick Start Guide

Get the QBI Visualizer running in 3 simple steps!

## Prerequisites

- Python 3.10+ (but < 3.13)
- Node.js 18+
- Git

## Method 1: One-Command Start (Recommended)

```bash
cd /Users/pavelmakarchuk/qbi-visualizer
./start.sh
```

This script will:
1. Set up Python virtual environment
2. Install all Python dependencies
3. Install all Node dependencies
4. Start backend on http://localhost:8000
5. Start frontend on http://localhost:5173

Press `Ctrl+C` to stop both services.

## Method 2: Manual Start

### Terminal 1 - Backend

```bash
cd /Users/pavelmakarchuk/qbi-visualizer/backend
pip install -e .
python -m app.main
```

### Terminal 2 - Frontend

```bash
cd /Users/pavelmakarchuk/qbi-visualizer/frontend
npm install
npm run dev
```

## What You'll See

1. **Backend Terminal**: Will show FastAPI starting up, then cloning policyengine-us from GitHub (first run only)
2. **Frontend Terminal**: Will show Vite dev server starting
3. **Browser**: Navigate to http://localhost:5173 to see the visualizer

## First Run Notes

- **First run takes ~2 minutes** while the backend clones policyengine-us from GitHub
- **Subsequent runs are instant** because data is cached
- The backend automatically parses all QBI Python files and extracts metadata

## Using the Visualizer

### Main Features

1. **Left Panel - Variable List**
   - Browse all QBI-related variables
   - 🔵 Blue = Input variables (no formula)
   - 🟡 Yellow = Intermediate calculations
   - 🟢 Green = Final output

2. **Center Panel - Variable Details**
   - Click any variable to see:
     - Metadata (entity, type, etc.)
     - Direct GitHub link to source code
     - Dependencies (what it uses)
     - Formula source code

3. **Sync Button**
   - Click "⟳ Sync" to pull latest changes from policyengine-us master
   - Updates automatically

### Example Workflow

1. Open http://localhost:5173
2. Wait for variables to load (~5 seconds on first run, instant thereafter)
3. Click "qualified_business_income" in the left panel
4. See its formula, dependencies, and GitHub link
5. Click on a dependency (e.g., "self_employment_income") to navigate there
6. Click "View on GitHub" to see the actual source code

## Complete Flow Visualization

The visualizer shows this complete flow:

```
INPUT VARIABLES (17 total)
├── 6 income sources
├── 6 qualification flags
├── 3 QBI deductions
├── 2 business properties
└── 3 tax unit inputs
          ↓
INTERMEDIATE VARIABLES (2)
├── qualified_business_income (Person)
└── qbid_amount (Person)
          ↓
OUTPUT VARIABLE (1)
└── qualified_business_income_deduction (TaxUnit)
```

## All Parameters Shown

The system tracks these 10 parameters:

1. `gov.irs.deductions.qbi.income_definition` - List of 6 income sources
2. `gov.irs.deductions.qbi.deduction_definition` - List of 3 deduction types
3. `gov.irs.deductions.qbi.max.rate` - 20% base rate
4. `gov.irs.deductions.qbi.max.w2_wages.rate` - 50% wage cap
5. `gov.irs.deductions.qbi.max.w2_wages.alt_rate` - 25% alt wage cap
6. `gov.irs.deductions.qbi.max.business_property.rate` - 2.5% property rate
7. `gov.irs.deductions.qbi.phase_out.start[filing_status]` - Income threshold
8. `gov.irs.deductions.qbi.phase_out.length[filing_status]` - Phase-out range
9. `gov.irs.deductions.qbi.deduction_floor.in_effect` - Boolean (2026+)
10. `gov.irs.deductions.qbi.deduction_floor.amount` - Bracket-based floor

## Troubleshooting

### "Failed to load variables"
- Make sure backend is running (check http://localhost:8000/health)
- Check backend terminal for errors

### "Connection refused"
- Backend might not be started
- Check if port 8000 is already in use: `lsof -i :8000`

### "Port 5173 already in use"
- Another dev server is running
- Kill it: `lsof -ti:5173 | xargs kill -9`

### Backend won't clone policyengine-us
- Check internet connection
- GitHub might be rate-limiting (wait 15 mins)
- Clone manually:
  ```bash
  cd backend/data/repos
  git clone https://github.com/PolicyEngine/policyengine-us.git
  ```

## Next Steps

Once you have it running:

1. **Explore Variable Dependencies**: Click through the dependency chains
2. **View GitHub Source**: Click "View on GitHub" to see actual code
3. **Sync for Updates**: Use "⟳ Sync" to get latest PolicyEngine changes
4. **Compare with TAXSIM**: Future feature - side-by-side comparison

## API Documentation

Backend API is available at: http://localhost:8000/docs

Key endpoints:
- `GET /api/variables/` - List all variables
- `GET /api/variables/{name}` - Get specific variable
- `GET /api/variables/graph/dependency` - Dependency graph
- `POST /api/variables/sync` - Sync from GitHub

## Full Documentation

For detailed setup, configuration, and development instructions:
- See `SETUP.md` for comprehensive guide
- See `README.md` for architecture and features

## Support

If you encounter issues:
1. Check backend terminal for Python errors
2. Check frontend browser console (F12) for JavaScript errors
3. Try clearing cache: `rm -rf backend/data/cache/* backend/data/repos/*`
4. Restart both services

## That's It!

You now have a complete visualization tool showing:
- ✅ All 17 QBI input variables
- ✅ All 2 intermediate calculations
- ✅ Final output deduction
- ✅ All 10 parameters used in formulas
- ✅ Direct GitHub links to source code
- ✅ Complete dependency tracking
- ✅ Always synced to latest PolicyEngine US master branch

Happy exploring! 🎉
