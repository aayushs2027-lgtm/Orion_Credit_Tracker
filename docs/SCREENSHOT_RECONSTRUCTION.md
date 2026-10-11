# Screenshot reconstruction

All 20 pages were inspected visually. The PDF contains no extractable text. Original images are retained locally under tmp/pdfs (ignored).

Navigation order: Command Center; Document Intake & Onboard; Customer Search; Customer History & Match; Personal Underwriting; Business Underwriting; Risk Intelligence & Fusion; Collateral Lab; Fraud & Network Graph; Scenario Lab (Monte Carlo); Loan Sizing & RAROC; Portfolio Intelligence; Explainability & SHAP; Review Queue & Workbench; Model Governance; Audit Trail.

|Page|Screen and navigation position|Visible components and workflow|Backend needed|Confidence / assumptions|
|---|---|---|---|---|
|1|Command Center, 1|Six KPI cards, selected borrower decision card, PD/LGD/loss, pipeline, discrepancy feed; rerun, document request, override, approve, decline|Aggregates, assessment and review APIs|High layout confidence; values are examples, not evidence|
|2|Intake identity, 2|Five-step bar; personal/business toggle; identity, employer, address, salary, obligation, loan fields; continue|Validated customer/application creation|High; fields inferred where tiny|
|3|Intake upload, 2|Dropzone, browse, document rows, extraction confidence, validate button|Restricted uploads, text extraction, OCR fallback|High|
|4|Intake field audit, 2|Extracted salary/employer fields, accept/edit/flag controls|Field provenance, corrections and audit|High; exact supported source templates unknown|
|5|Intake matching, 2|Entity match result, launch case and underwriting|Fuzzy match, discrepancy flags|High|
|6|Intake underwriting, 2|Final selected step with empty workspace|Assessment execution and navigation|Low content confidence; screenshot shows no final result|
|7|Customer Search, 3|Search, product filters, grade filter, registry table, open case|Search, filters, pagination and selection|High|
|8|Customer History & Match, 4|Side-by-side current/historic values, change highlights, timeline, past loans|Persistent snapshots, repayments, reviews, audit|High|
|9|Personal Underwriting, 5|ML execution trace, unsecured product policy, income shock slider, bureau dossier, tradelines, cash flow|Financial calculations, model inference, bureau parsing, scenario|High; no live bureau implied|
|10|Business Underwriting, 6|ML trace, quantitative/qualitative/collateral triad, revenue/margin/rate sliders, financial ratios|Business inputs, ratio calculation, stress API|High; custom triad weights unknown|
|11|Risk Intelligence & Fusion, 7|Credit vs data integrity scores, confidence cards, survival curve|PD/LGD/EAD/loss, separate discrepancy scoring|Medium; survival model parameters not supplied, do not fabricate|
|12|Collateral Lab, 8|Value, haircuts, liquidation value, LTV, pledged asset table|Valuations and recovery assumptions|High|
|13|Fraud & Network Graph, 9|Customer selector tiles, shared KYC entity graph, address chronology|Entity linkage and investigations|High; graph flags are not fraud verdicts|
|14|Scenario Lab, 10|Macro regimes, iteration selector, correlation slider, EL/VaR/CVaR, loss histogram, reset|Seeded correlated Monte Carlo|High; screenshot numeric outputs unverified|
|15|Loan Sizing & RAROC, 11|Requested/optimal amount, rate, annual margin, counterfactual intervention, covenants|Constrained sizing, expected loss, RAROC|High; economic capital assumptions must be disclosed|
|16|Portfolio Intelligence, 12|Before/after impact table, sector exposure bars, rating migration table|Stored exposure aggregation|Medium; no observed migration history, omit invented matrix|
|17|Explainability & SHAP, 13|SHAP waterfall, decision trace, provenance table|Actual SHAP values and source mapping|High|
|18|Review Queue & Workbench, 14|Customer tiles, discrepancy tabs, accept/edit/resolve workbench|Reviewer RBAC, investigation status, decision history|High; detailed editor not visible|
|19|Model Governance, 15|Candidate benchmark, hyperparameters, calibration/CV/features/error/defense tabs|Versioned training results, evaluation and docs|High; do not reproduce supplied metrics as measured results|
|20|Audit Trail, 16|Search, ledger table, JSON export, integrity indicator|Chained audit events, integrity verification|High|

Shared design: white topbar, narrow white left navigation, very pale blue-grey workspace, navy text and indigo controls, thin borders, compact financial tables, selected customer in header, research prototype label. Improve readable type sizes and responsive layout. Every implemented button must invoke actual navigation, calculation, persistence or export.
