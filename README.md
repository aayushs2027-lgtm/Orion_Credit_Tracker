# ORION — Enterprise Credit Intelligence & Underwriting

Local Python-powered academic credit decision product. React/TypeScript interface reconstructs the 16 workspaces in the supplied screenshot reference. Financial calculations, document processing, matching, ML training/inference, simulations and workflow persistence run in Python. All demonstration customers and training outcomes are fictional.

## Open the installed application

Visit **http://127.0.0.1:8000**. Username **admin**; the locally generated password is in **D:\ORION\.env** under `ORION_ADMIN_PASSWORD`. The initial demo accounts `reviewer`, `analyst`, and `viewer` share this password; they have different API permissions. New users can be created by an administrator in Model Governance.

The server listens only on loopback. `scripts/start.ps1` starts it again after closing the current background process or restarting the computer. It does not silently kill processes using the port. Do not run two ORION instances against one SQLite database.

## Fresh setup (PowerShell, Python 3.12 and Node.js)

1. Run `powershell -ExecutionPolicy Bypass -File scripts/setup.ps1` from this folder. This installs dependencies, builds the frontend, applies migrations, trains missing models and seeds fictional data. Internet access is needed for initial dependencies.
2. Run `powershell -ExecutionPolicy Bypass -File scripts/start.ps1`.
3. Open the address above. No paid AI key is needed.

The setup script uses system Python/Node/pnpm or the bundled Codex runtimes if available. Frontend dependency versions are locked in `frontend/pnpm-lock.yaml`; Python in `requirements-lock.txt`. The virtual environment stays inside the project. Seed is idempotent and never resets existing records.

## Verification

```
.venv\Scripts\python.exe -m pytest -q
cd frontend
pnpm test
pnpm build
pnpm exec playwright install chromium
pnpm exec playwright test
```

Browser tests need the server running and the project's `.env` credentials. They create clearly named fictional Browser Demo/Business records in the local demo database; API tests use separate temporary databases. See `docs/TEST_REPORT.md` for the actual results, environment details and nonfatal warnings. Browser screenshots are in `docs/screenshots`.

## Core workflows

- **Personal:** intake → create borrower/facility → upload sample TXT/PDF → accept/correct extraction → apply fields → assessment → SHAP → human review/override → audit and credit memo.
- **Business:** select business intake, enter annual figures → register collateral for secured facilities → calculate DSCR and other ratios → select a trained algorithm → scenario/structure comparison → human decision.
- **Returning customer:** search/open case → History or Underwriting → update address or financial snapshot → income jumps ≥2x and address changes create investigation flags → reviewer records resolution.
- **Portfolio:** filter assessed pipeline by product, inspect sector/risk exposure, compare disbursed balances separately, run correlated downturn simulation, export CSV.
- **Governance:** train all three candidate models; inspect actual held-out metrics, calibration and errors; record validation notes, activate a version, create role-scoped users.

Supported credit-report template and sample financial statements are under `sample_data/`. Uploaded reports are not live bureau queries. Account-line import is explicit after source review. Extracted financial fields are applied only after acceptance/correction. Scanned documents need Tesseract; the current machine has no Tesseract executable. Such PDF pages are honestly marked for manual review.

## Project layout

- `backend/`: API, relational models, migrations, security, document and financial services.
- `src/data.py`, `src/model.py`, `app.py`: assignment-compatible modular dataset, ML and ASGI entry points.
- `frontend/`: React app, unit tests, Playwright journeys.
- `scripts/`: setup, start, seed and train entry points.
- `tests/`: Python finance/security/API/ML workflow tests.
- `docs/`: reference mappings, architecture, algorithms, business presentation outline, limitations and verification.
- `data/`, `artifacts/`, `.env`: ignored local state, uploads, models and credentials.

## Academic scope and remaining limits

This is a working local academic product, not a certified banking system. The initial synthetic ML dataset has 1,800 rows and is intentionally reproducible; its measured metrics cannot establish real-world lending performance. PD has no empirically calibrated time horizon, LGD/recovery/capital/funding inputs are illustrative. No live bureau, external LLM, fairness certification, regulatory compliance, or realized ROI is claimed. See `docs/KNOWN_LIMITATIONS.md` for the explicit boundaries.

GitHub publication and the team's 15-minute presentation/Q&A are not performed automatically. The editable deck is `output/presentation/ORION_Academic_Defense.pptx` (13 slides, speaker notes, editable architecture/table/chart evidence). `docs/PRESENTATION_AND_DEMO.md` provides the timing and live-demo guide. The deck package/layout/import and all final slide previews were verified, but it was not opened in Microsoft PowerPoint.
