# Executed verification

## Latest refinement validation — 12 October 2026

- Python: **21 passed** (5.85s), including multiple-source address conflicts, source provenance, idempotent re-review, formatting normalization, evidence/manager approval gates, immutable approved findings, unchanged original model assessment, escalation-team requirement, whitespace rejection and outstanding finding count consistency. Revenue cases exercise below/at/above 200%, zero-base positive and zero revenue, repeated snapshots and nonconsecutive-year rejection.
- Frontend: **4 unit tests passed**; finance display conventions plus title-case status/acronym formatting. TypeScript and Vite production build passed.
- Chromium: **5 workflows passed** (7.9s on the final run). Added address evidence escalation → verification → manager sign-off and business prior-year revenue input → visible 400% review finding. Existing intake, navigation, inference, reports, exports and mobile scenario workflows still pass.
- Visual inspection: refreshed Command Center and investigation desktop/mobile captures; added revenue-verification capture. Mobile horizontal-overflow checks pass at 390px and 780px.
- Existing nonblocking warnings: Starlette/httpx test-client deprecation and React Router ignored `use client` bundler directives. No dependency changes made.

Earlier baseline results below are retained as implementation history.

Date: 12 October 2026, Asia/Calcutta. Environment: Windows, Python 3.12 dedicated .venv, Node.js 24 bundled runtime, pnpm 11.25.0, Chromium via Playwright. Tests run against actual local services and model artifacts.

|Check|Executed result|
|---|---|
|Alembic upgrade head|Passed, local SQLite at revision 002|
|Fictional seed/training|Passed; 10 initial customers, 3 tuned models, stored measured metrics|
|Fresh seed verification|Passed in separate temporary DB: 10 customers, explicit human override, disbursed facility and intact audit chain; current demo DB left unchanged|
|pytest -q|14 passed, 4.57s on final recorded run|
|pnpm build|TypeScript passed, Vite production build passed, 3 chunks; no CSS errors|
|pnpm test|2 display-semantics unit tests passed|
|pnpm exec playwright test|3 passed, 5.4s on latest run|
|Visual QA|Command Center, Governance and Scenario mobile PNGs individually inspected; no clipping or horizontal viewport overflow in tested mobile layout|
|Academic deck|13 slides; package/layout findings 0; native chart/workbook checks passed; final file imported and all 13 final PNG previews visually inspected|

## Python coverage exercised

- Known EMI example, zero interest, invalid tenure and zero denominator handling.
- Business DSCR/current ratio/leverage, unsecured collateral policy and EL identity.
- Monte Carlo repeatability/tail ordering and revenue/expense/income shock arithmetic.
- Persistent personal intake, TXT upload, extracted-field acceptance/correction, application assessment, linked human override and locked final decision.
- Business collateral LGD, DSCR stress and persisted structure alternatives.
- Income tripling/address change flags, resolution, identity uniqueness and exact matching, CUS/application/name search.
- Authentication, viewer/analyst authorization, admin-only training, untrusted browser origin, invalid loan/scenario values and rejected executable/spoofed PDF uploads.
- Aggregate portfolio consistency, stress API, JSON/CSV exports, model metadata and repeatable inference.
- Actual SHAP additivity for Logistic Regression, Random Forest and XGBoost.
- Supported bureau account import, duplicate import rejection, approval prerequisite for disbursement, repayment principal limits and outstanding reduction, validation note and new-user persistence.
- Generated text PDF extraction with page/evidence provenance, invalid correction rejection, accepted corrected income application.
- Audit-chain integrity and deliberate in-memory tampering detection; rejected unauthorized approval leaves workflow unchanged.

## Chromium coverage exercised

1. Sign in, all 16 navigation routes, measured governance display, personal borrower and facility creation, document upload, accept/apply field, model inference, explicit human override, audit integrity, actual download and customer search.
2. Stored business case revenue shock, Python stress and Monte Carlo output, mobile viewport screenshot, no horizontal page overflow.
3. New secured business intake, document upload, collateral registration, explicit XGBoost assessment, DSCR display, reviewed credit-account import, actual SHAP workspace and SPA refresh.

Screenshots: docs/screenshots/command-center.png, governance.png, scenario-mobile.png. Browser runs retain fictional records; Python tests create isolated DB files and remove those after success.

## Failures found and resolved

Initial package network/temporary-directory sandbox failures; approved dependency execution and workspace tmp resolved them. Sandbox Python workers stalled and pnpm could not traverse package junctions; approved local execution completed verification. TypeScript untyped callback fixed. One initial API test failed from Field class shadowing; corrected import. Vitest initially collected the Playwright suite; src-only test config fixed it. CSS import removal initially left a font URL fragment; removed, rebuilt and retested. All listed current suites passed after fixes.

## Unverified / unavailable

OCR execution (Tesseract absent), Docker (binary absent), PostgreSQL integration, public deployment, production-load/concurrency testing, real credit data validation, external bureau/LLM integration, and actual PowerPoint application rendering. Deck export initially found font-policy/runtime configuration errors, corrected before final delivery. The successful finalizer emitted all passing receipts but its initial authoring process returned a nonzero exit after printing its receipt; a separate final-file import, full rendering and ZIP verification command then exited 0.

Nonfatal warnings: Starlette httpx TestClient deprecation; React Router `use client` bundling directives ignored; Playwright NO_COLOR/FORCE_COLOR environment warning. These did not prevent passing tests.
