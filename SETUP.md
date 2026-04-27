# QBI Visualizer - Setup Guide

Complete setup instructions for the QBI Computation Visualizer.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher** (but < 3.13)
- **Node.js 18 or higher**
- **Git**
- **pip** (Python package manager)
- **npm** (comes with Node.js)

Check your versions:
```bash
python3 --version  # Should be 3.10, 3.11, or 3.12
node --version     # Should be 18+
npm --version
git --version
```

## Quick Start

### 1. Navigate to Project

```bash
cd /Users/pavelmakarchuk/qbi-visualizer
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Copy environment template
cp .env.example .env

# Install Python dependencies
pip install -e .

# The backend will automatically:
# - Clone policyengine-us from GitHub on first run
# - Extract QBI variable metadata
# - Cache results for faster subsequent loads
```

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install Node dependencies
npm install

# This installs React, Tailwind CSS, and visualization libraries
```

### 4. Run the Application

You need TWO terminal windows:

**Terminal 1 - Backend:**
```bash
cd /Users/pavelmakarchuk/qbi-visualizer/backend
python -m app.main
# Or: uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd /Users/pavelmakarchuk/qbi-visualizer/frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 5. Open in Browser

Navigate to: **http://localhost:5173**

You should see:
- QBI variables listed in the left panel
- Click any variable to see details
- GitHub links for source code
- Dependency information

## First Run

On first run, the backend will:

1. Clone `policyengine-us` from GitHub (takes ~1 minute)
2. Parse all QBI-related Python files using AST
3. Extract variable metadata, formulas, and dependencies
4. Cache results in `backend/data/cache/`

Subsequent runs will use the cache and start instantly.

## Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Keep default for always-latest
GITHUB_BRANCH=master

# Adjust if you want different update frequency
AUTO_SYNC_MINUTES=30

# Optional: Add TAXSIM integration
TAXSIM_PATH=/path/to/your/taxsim
TAXSIM_EXECUTABLE=taxsim35
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` via Vite proxy.

If you need to change ports, edit `frontend/vite.config.ts`:

```typescript
server: {
  port: 5173,  // Change frontend port
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // Change backend URL
      changeOrigin: true,
    },
  },
},
```

## Usage

### Viewing Variables

1. **Left Panel**: Browse all QBI variables
   - 🔵 Blue = Input variables (no formula)
   - 🟡 Yellow = Intermediate calculations
   - 🟢 Green = Final output (qualified_business_income_deduction)

2. **Center Panel**: Click a variable to see:
   - Metadata (entity, type, etc.)
   - GitHub link to source code
   - Dependencies (what it depends on)
   - Used by (what depends on it)

### Syncing from GitHub

Click the **⟳ Sync** button in the top-right of the left panel to:
- Pull latest changes from policyengine-us master branch
- Re-extract all variables
- Update the view with any new changes

### Exploring Dependencies

- Click any variable name in the dependencies list to navigate to that variable
- Build a mental model of how inputs flow to outputs

## API Endpoints

The backend provides these endpoints:

- `GET /` - Health check
- `GET /api/variables/` - List all QBI variables
- `GET /api/variables/{name}` - Get specific variable details
- `GET /api/variables/graph/dependency` - Get dependency graph
- `POST /api/variables/sync` - Sync from GitHub

Test the API directly:
```bash
# List all variables
curl http://localhost:8000/api/variables/

# Get specific variable
curl http://localhost:8000/api/variables/qualified_business_income

# Sync from GitHub
curl -X POST http://localhost:8000/api/variables/sync
```

## Directory Structure

```
qbi-visualizer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── api/
│   │   │   └── variables.py     # Variables API endpoints
│   │   ├── services/
│   │   │   ├── github_manager.py    # GitHub operations
│   │   │   ├── code_extractor.py    # Python AST parser
│   │   │   └── parameter_extractor.py  # YAML parser
│   │   └── models/
│   │       └── variable.py      # Pydantic models
│   ├── data/
│   │   ├── repos/               # Cloned policyengine-us (created automatically)
│   │   └── cache/               # Cached extraction results
│   ├── pyproject.toml
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── App.tsx              # Main app component
│   │   └── pages/
│   │       └── FlowView.tsx     # Variables view
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
└── README.md
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
cd backend
pip install -e .
```

**Error**: `git.exc.GitCommandError`
- Check internet connection
- GitHub might be rate-limiting: wait 15 minutes and try again

### Frontend won't start

**Error**: `Cannot find module 'react'`
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `Port 5173 already in use`
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9
# Or change port in vite.config.ts
```

### Variables not loading

1. Check backend is running: `curl http://localhost:8000/health`
2. Check browser console for errors (F12)
3. Try syncing: Click "⟳ Sync" button
4. Clear cache:
   ```bash
   rm -rf backend/data/cache/*
   rm -rf backend/data/repos/*
   # Restart backend
   ```

### GitHub sync failing

**Error**: `Failed to sync repository`
- Check internet connection
- Verify GitHub URL in `.env` is correct
- Try cloning manually:
  ```bash
  cd backend/data/repos
  git clone https://github.com/PolicyEngine/policyengine-us.git
  ```

## Development

### Backend Development

Auto-reload is enabled:
```bash
cd backend
uvicorn app.main:app --reload
```

Any changes to Python files will automatically restart the server.

### Frontend Development

Hot module replacement is enabled:
```bash
cd frontend
npm run dev
```

Any changes to React files will instantly update in the browser.

### Adding New API Endpoints

1. Create new router in `backend/app/api/`
2. Add router to `backend/app/main.py`:
   ```python
   from app.api import my_new_router
   app.include_router(my_new_router.router, prefix="/api/my-route")
   ```

### Adding New Frontend Pages

1. Create component in `frontend/src/pages/`
2. Import and use in `App.tsx`

## Next Steps

Once you have the basic visualizer running, you can:

1. **Add Parameter Display**: Show parameter values from YAML files
2. **Add Calculation Engine**: Run actual PolicyEngine calculations
3. **Add TAXSIM Comparison**: Compare PE results with TAXSIM
4. **Add Graph Visualization**: Use React Flow to show dependency graph
5. **Add Export Features**: Export flows as PNG/SVG

## Support

For issues specific to this visualizer, check:
- Backend logs in the terminal running uvicorn
- Frontend console (F12 in browser)
- Network tab (F12 → Network) to see API calls

For PolicyEngine US issues:
- GitHub: https://github.com/PolicyEngine/policyengine-us
- Documentation: https://policyengine.org/us/docs

## License

MIT License - See LICENSE file
