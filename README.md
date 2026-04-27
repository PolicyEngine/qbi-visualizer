# QBI Computation Visualizer

A comprehensive visualization tool for the Qualified Business Income Deduction (Section 199A) calculation in PolicyEngine US.

## Features

- **Complete Input-to-Output Flow Visualization**: Shows all input variables flowing through to the final QBI deduction
- **Dynamic GitHub Integration**: Automatically pulls latest PolicyEngine US code from master branch
- **Parameter Visibility**: Displays all parameters used in formulas with direct links to YAML files
- **Interactive Dependency Graph**: Click any variable to see its formula, dependencies, and references
- **Legal References**: Direct links to USC statutes, IRS forms, and publications
- **TAXSIM Comparison**: Compare PolicyEngine calculations against TAXSIM (optional)

## Architecture

### Backend (FastAPI + Python)
- **GitHub Manager**: Clones and syncs policyengine-us from GitHub
- **Code Extractor**: Dynamically parses Python variables using AST
- **Parameter Extractor**: Extracts parameter values from YAML files
- **Calculator**: Runs actual PolicyEngine calculations with intermediate steps
- **API**: REST endpoints for variables, parameters, calculations, and comparisons

### Frontend (React + TypeScript)
- **Flow Visualization**: Interactive computation graph showing inputs → outputs
- **Variable Details Panel**: Shows formulas, dependencies, parameters, and references
- **Input Controller**: Set scenario inputs and run calculations
- **Comparison View**: Side-by-side PolicyEngine vs TAXSIM results

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup

```bash
cd backend
pip install -e .
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173

## Configuration

Create `backend/.env`:

```bash
# GitHub Configuration
GITHUB_REPO=https://github.com/PolicyEngine/policyengine-us.git
GITHUB_BRANCH=master
AUTO_SYNC_MINUTES=30

# Local Paths
REPOS_DIR=./data/repos
CACHE_DIR=./data/cache

# TAXSIM Integration (Optional)
TAXSIM_PATH=/path/to/taxsim
TAXSIM_EXECUTABLE=taxsim35
```

## Usage

1. **View Complete Flow**: See all QBI inputs → final deduction with parameters
2. **Click Variables**: View source code, formulas, and GitHub links
3. **Click Parameters**: See YAML files, values, and legal references
4. **Run Calculations**: Enter scenario inputs and see step-by-step results
5. **Compare with TAXSIM**: Run same scenario through both systems

## QBI Deduction Components

### Input Variables (17)
- 6 income sources (self-employment, partnership, rental, farm ops, farm rent, estate)
- 6 qualification flags (would_be_qualified for each income source)
- 3 QBI deductions (SE tax, health insurance, pension)
- 2 business properties (W-2 wages, property basis)
- 2 business type flags (is_sstb, is_qualified)
- 3 tax unit inputs (taxable income, filing status, capital gains)

### Parameters (10)
- Income and deduction definition lists
- 4 rates (base 20%, wage 50%, alt wage 25%, property 2.5%)
- 2 phase-out parameters (start threshold, length)
- 2 deduction floor parameters (in_effect, amount)

### Output
- Final qualified_business_income_deduction at tax-unit level

## Project Structure

```
qbi-visualizer/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuration
│   │   ├── api/                    # API endpoints
│   │   │   ├── variables.py
│   │   │   ├── parameters.py
│   │   │   ├── calculate.py
│   │   │   └── compare.py
│   │   ├── services/               # Core services
│   │   │   ├── github_manager.py
│   │   │   ├── code_extractor.py
│   │   │   ├── parameter_extractor.py
│   │   │   ├── calculator.py
│   │   │   └── cache_manager.py
│   │   ├── models/                 # Pydantic models
│   │   └── utils/                  # Utilities
│   ├── scripts/                    # One-time scripts
│   ├── data/                       # Git repos, cache
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Main views
│   │   │   ├── FlowView.tsx
│   │   │   ├── TableView.tsx
│   │   │   └── ComparisonView.tsx
│   │   ├── components/             # UI components
│   │   │   ├── FlowGraph.tsx
│   │   │   ├── VariableDetail.tsx
│   │   │   ├── InputPanel.tsx
│   │   │   └── ParameterDisplay.tsx
│   │   ├── hooks/                  # React hooks
│   │   └── types/                  # TypeScript types
│   └── public/
└── docs/
```

## Development

### Adding New Variables
The system automatically detects new QBI-related variables when syncing from GitHub.

### Updating Parameters
Parameter values are extracted dynamically from YAML files in the policyengine-us repo.

### Customizing Visualization
Edit `frontend/src/components/FlowGraph.tsx` to change the flow diagram layout.

## Legal References

- **26 USC § 199A**: Qualified Business Income Deduction
- **IRS Publication 535**: Business Expenses (Worksheet 12-A)
- **Form 8995**: Qualified Business Income Deduction Simplified Computation
- **Form 8995-A**: Qualified Business Income Deduction (detailed)

## Contributing

This is a visualization and analysis tool. To contribute to the underlying PolicyEngine US calculations, see [PolicyEngine/policyengine-us](https://github.com/PolicyEngine/policyengine-us).

## License

MIT License - See LICENSE file for details

## Credits

Built to visualize and understand the QBI deduction implementation in PolicyEngine US.
