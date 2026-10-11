# 15-minute presentation and live demonstration outline

This is preparation material, not a generated slide deck or a record of a delivered presentation.

## Executive pitch — 5 minutes

1. Problem/persona (1 minute): credit analysts and committee reviewers spend time reconciling borrower documents, financial capacity and model recommendations. ORION joins those steps with traceable human decisions.
2. Product (1 minute): show Command Center, Intake, Underwriting and Review. Use the fictional-data badge to establish academic scope.
3. Business value (2 minutes): Governance → Technical Defense → business case. Hypothetical 1,000 cases/month ×30 minutes saved ×INR600/hour = INR3,600,000 annual labor value; less INR150,000 annual operating cost = INR3,450,000 net; ROI=2,300%. These are scenario assumptions, not realized results. Explain sensitivity and exclude unsupported default-reduction claims.
4. Market strategy (1 minute): start with an internal educational analyst workbench; validate with anonymized authorized real outcomes before any controlled lending pilot. Reviewer workflow, explainability and reconciliation are the initial differentiators. No compliance claim.

## Technical deep dive — 10 minutes

- Architecture (2 min): use ARCHITECTURE diagram. React → FastAPI → finance/ML/documents → SQLAlchemy; versioned model artifacts and audit.
- Feature choices (1 min): score, repayment burden, delinquencies, utilization, stability and product. Explain annual/monthly conversions and missing-denominator handling.
- Optimization and validation (2 min): three algorithms, stratified 80/20 split, 5-fold training CV, grids, scaling inside pipeline, model selection without test peeking, calibration/Brier and confusion matrix. Read current actual metrics from Governance rather than assuming static numbers.
- Explainability/errors (2 min): select model in underwriting; SHAP base+contributions reconstructs probability or log odds. Explain cost of false positives vs negatives, threshold .30, synthetic-data limits.
- Live demonstration (3 min): new personal borrower, upload sample report, review/apply fields, assess, display explanations, reviewer decision and audit. Pre-stage a business case to show DSCR, collateral LGD and downturn simulation quickly.

## Extended demo paths

**A — personal:** Intake; unique DEMO-NEW identity; INR120,000 monthly income, INR10,000 existing EMI, INR1,000,000 request/12%/60 months; unsecured. Upload sample_data/personal_credit_report.txt; inspect/accept fields; apply; launch. Explain EMI/DTI/PD/LGD/loss. Review and override if different from model, with administrator and reason. Download credit memo.

**B — business:** Business intake; INR24m revenue, INR4m EBITDA, INR3.2m cash flow; create secured facility. Collateral Lab: INR2m property, haircut .25, valid date. Underwriting: edit annual debt/interest/liquidity/equity figures; choose XGBoost; assess; inspect actual SHAP. Scenario Lab: revenue −20%, costs +10%, rate +2pp. Loan Sizing: compare alternatives. Review.

**C — returning:** Open Arjun Mehta or create a borrower, then update income to 3×. History exposes snapshots; Review Queue shows discrepancy, enter supporting-evidence reason and resolve. An address change similarly creates a flag. These are verification leads, never fraud declarations.

**D — portfolio:** Portfolio Intelligence shows assessed pipeline vs separately recorded disbursements. Filter products; inspect sector/risk breakdown; run downturn simulation and export CSV. Explain Gaussian correlation and discrete losses. Audit export verifies stored event sequence.

## Q&A preparation

- Why is absent collateral allowed for unsecured loans? Product design; it affects LGD, not automatic rejection.
- Are metrics real? They are executed held-out metrics on synthetic educational data, not field validation.
- Is SHAP causal? No, it attributes model output relative to a background reference.
- How is leakage prevented? Train/test split precedes tuning; scaling fits within CV pipelines; target never enters features.
- Why no official CIBIL score API? Only uploaded reported scores and stored values are supported.
- What breaks at enterprise scale? Synchronous jobs, single SQLite process, simple entity graph, local audit anchoring; see limitations and deployment roadmap.
- How is original recommendation protected? Immutable-by-API assessment rows and linked review/override records.
- Why synthetic PD horizon? No loan-outcome data or calibrated horizon was supplied; don't interpret EL as IFRS9 or Basel capital.

Assign the pitch, architecture, modeling, finance, document workflow, security, validation and demo/Q&A across the team's 8–9 members. Each member should be able to explain all core choices, as required by the assignment.
