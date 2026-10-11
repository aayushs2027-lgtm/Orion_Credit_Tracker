# ORION implementation plan

## Reference analysis completed
Assignment: `references/Applied_AI_Data_Science_Group_Project.docx.pdf`, 3 pages, fully extracted. Screenshots: `references/Screenshot 2026-10-12 010708.pdf`, 20 image-only pages, all visually inspected using extracted page images; pages 1 and 19 inspected at native resolution.

## Incremental delivery
1. Foundation: Python 3.12 virtual environment, FastAPI, SQLAlchemy, SQLite, Alembic; React/TypeScript/Vite; authentication and seeded fictional records.
2. Core: persistent customers, applications, history, document uploads, extracted field review, entity matching.
3. Finance: personal/business underwriting, collateral, expected loss, scenarios and constrained loan sizing.
4. ML: reproducible synthetic dataset, held-out test set, cross-validation and tuning of Logistic Regression, Random Forest, XGBoost, SHAP, persisted versioned artifacts and real inference.
5. Decisions: review, overrides with original assessment retained, investigations, audit, portfolio and exports.
6. Verification: financial unit tests, API integration journeys, frontend build and browser workflow verification; publish accurate limitations and demo instructions.

## Decisions and boundaries
- Assignment has priority. Add root app.py and src/data.py, src/model.py adapters to preserve its requested repository entry points.
- No evidence for the screenshot's performance, regulatory badges or custom model claims: do not copy those claims.
- Synthetic training and seed data are conspicuously labelled educational. No live credit bureau or paid LLM integration.
- Preserve 16 screenshot navigation sections; embed bureau intelligence and expected loss within underwriting and risk modules.
- Source images do not establish hidden interactions or training data: use documented explicit assumptions.
- GitHub publication and a 15-minute live team presentation remain external deliverables; prepare local presentation/defense material without claiming submission.

## Current status
Phases 0–10 have local implementations and executed core workflow checks. Source, migrations, training, tests, reference mapping, algorithm/architecture documentation, setup scripts and an editable 13-slide academic deck are delivered. The full enterprise vision still has explicit deployment/data/document-depth limitations rather than claimed certification; see KNOWN_LIMITATIONS. GitHub publication and live team presentation remain external. See IMPLEMENTATION_LOG and TEST_REPORT for measured verification.
