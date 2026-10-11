# Explicit limitations and remaining work

## Working local scope

The 16 screenshot navigation workspaces are implemented and connected to persistent APIs. New personal/business customers and facilities, document text extraction and correction, exact/fuzzy matching, financial snapshots, assessments with any of three trained models, SHAP, collateral, expected loss, scenarios, structure comparison, portfolio, reviews, overrides, investigations, bureau tradelines, disbursement/repayment entry, user creation, model validation/activation, audit and exports work locally. See TEST_REPORT for executed evidence; it is not exhaustive certification of every possible input.

## Analytical limits

- All default training outcomes and initial customers are synthetic. No statistical model is externally validated or calibrated to real defaults or a specific PD horizon.
- No IFRS9 staging, survival model, migration model, demographic fairness claim, regulatory capital model or live credit bureau integration. These screenshot claims/charts were not copied without evidence.
- Loss assumptions, correlation, funding/capital and policy thresholds are illustrative and documented. Portfolio default simulation has fixed EAD/LGD and one Gaussian correlation parameter, without amortization, macro calibration or correlated recovery.
- Business interest coverage uses EBITDA and proposed first-year contractual interest as an explicit proxy. Documents do not undergo accounting restatement, tax verification or market valuation.
- Loan structuring searches a discrete tenure set under stated capacity/collateral constraints, with illustrative RAROC. It does not globally optimize commercial pricing/fees or enforce real bank product rules.
- Current customer profiles can change while historical assessments remain intact. Reassess pending facilities after input updates. Final decisions lock assessment and review actions, but a new application is needed for renewal.
- Scenario PD multipliers alter risk-policy output explicitly. SHAP still explains the raw model probability, not the external multiplier.

## Documents and data

- Text PDFs and UTF-8 TXT support explicit labelled fields. Account tradelines require the documented pipe-separated `Account:` template. Arbitrary layouts, handwriting, passwords/encrypted PDFs and bureau-vendor-specific tables do not have reliable automated extraction.
- Tesseract is not installed. Image uploads report the missing dependency; image-only PDF pages produce an honest manual-review notice. OCR integration exists but OCR execution has not been tested locally.
- Extraction confidence is a labelled heuristic, not calibrated field accuracy. Users must review values. Account imports are explicit source-review actions and do not automatically change financial obligations.
- Personal and business customers are logically distinct with typed financial profiles in shared tables, rather than the directive's suggested separate physical subtype tables. Some analytical snapshots use JSON; migration/database constraints and foreign keys protect core entities. There is no configurable product catalog or separate role catalog.
- Network display shows stored nodes and an evidence edge table rather than an interactive force-directed graph. Shared KYC attributes and fuzzy similarities require investigation.
- Portfolio exposure is an assessed requested-principal pipeline proxy. Disbursed outstanding is separate. Cohort trends group current status by creation month; no historical rating migration estimates are invented.

## Engineering and deployment

- Intended for one local server instance and SQLite. Model jobs and OCR are synchronous; no distributed job queue, concurrency/load testing or multi-tenant authorization.
- Audit chaining detects modification in the stored sequence, with no external anchoring. Privileged full rewrites/suffix removal are outside its guarantees. Application audit records have no edit/delete endpoints.
- Filesystem artifacts and database registry updates are not one atomic distributed transaction. A crash may leave an unregistered training folder or orphan upload.
- Basic upload restrictions do not replace anti-malware, decompression limits or sandboxed OCR needed for hostile internet uploads.
- Session cookies use local HTTP without the HTTPS-only Secure flag. TLS, centralized login limits, password reset/MFA, scoped data access, monitoring, backup/restore drills and secret management remain deployment work.
- Docker configuration is supplied but untested because Docker is unavailable. PostgreSQL-oriented ORM design exists, but the driver and a PostgreSQL migration/integration test are not installed/run.
- Frontend is a functional application with shared screen components in one main module; further component extraction would improve maintenance as the product grows. Unit tests focus on financial display semantics and backend behaviors, with Chromium journeys covering integration.
- Current dependency warnings: React Router's ignored bundler `use client` directives; Starlette's httpx TestClient deprecation; Playwright environment color warning. They are not reported as application failures.

## Academic handoff

The local repository, measured evaluation, algorithm documentation, AI development log and presentation preparation are provided. GitHub publication needs a destination and account authorization. The team must deliver the live demo and defend the algorithms itself. No public hosting or external publication occurred.
