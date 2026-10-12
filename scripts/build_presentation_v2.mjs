import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {Presentation,PresentationFile,FileBlob} from '@oai/artifact-tool';
const ROOT='D:/ORION',SKILL='C:/Users/Aayush/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs'));
const m=JSON.parse(await fs.readFile(ROOT+'/docs/MODEL_EVALUATION.json','utf8'));
const roi=JSON.parse(await fs.readFile(ROOT+'/tmp/deck/roi.json','utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});p.theme.defaultFont='Arial';
const C={navy:'#172544',blue:'#4c50be',teal:'#137d80',ink:'#273952',muted:'#627187',line:'#d7deea',paper:'#f6f8fc',white:'#ffffff',orange:'#c26c40'};
const tables=[],charts=[];
function txt(s,v,x,y,w,h,size=26,color=C.ink,bold=false){const z=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});z.text=v;z.text.style={typeface:'Arial',fontSize:size,color,bold};return z;}
function rect(s,x,y,w,h,fill,line='none'){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:line,width:line==='none'?0:1}});}
function line(s,x,y,w,h,color=C.line){s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:h},line:{fill:color,width:2}});}
function slide(title,note,section='TECHNICAL',dark=false){const s=p.slides.add();s.background.fill=dark?C.navy:C.paper;txt(s,section,64,29,950,26,16,dark?'#aebde5':C.blue,true);txt(s,title,64,76,1152,94,44,dark?C.white:C.navy,true);txt(s,'ORION   /   Synthetic academic demonstration',64,673,1010,22,15,dark?'#aebde5':C.muted);txt(s,String(p.slides.items.length).padStart(2,'0'),1170,673,55,22,15,dark?'#aebde5':C.muted);s.speakerNotes.text=note;return s;}
function table(s,vals,{x=64,y=190,w=1152,h=340,widths}={}){tables.push(p.slides.items.length);const t=s.tables.add({rows:vals.length,columns:vals[0].length,left:x,top:y,width:w,height:h,columnWidths:widths??vals[0].map(()=>w/vals[0].length),values:vals});for(let r=0;r<vals.length;r++)for(let c=0;c<vals[0].length;c++){const q=t.getCell(r,c);q.fill=r===0?C.navy:r%2?C.white:'#edf1f8';q.text.style={typeface:'Arial',fontSize:23,color:r===0?C.white:C.ink,bold:r===0};}return t;}
function chart(s,cats,series,{x=64,y=190,w=1152,h=360,fmt='0.000',legend=true}={}){charts.push(p.slides.items.length);const ch=s.charts.add('bar',{position:{left:x,top:y,width:w,height:h},categories:cats,series,hasLegend:legend,legend:{position:'bottom',textStyle:{fontSize:19}},barOptions:{direction:'column',grouping:'clustered'},xAxis:{textStyle:{fontSize:20}},yAxis:{numberFormatCode:fmt,min:0,...(fmt==='0.000'?{max:1}:{}),textStyle:{fontSize:19}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:fmt,textStyle:{fontSize:21,bold:true}}});applyPresentationChartFont(ch,{fontFamily:'Arial'});return ch;}
function row(s,num,title,body,y,{width=1040}={}){txt(s,num,64,y,65,60,39,C.blue,true);txt(s,title,150,y,width,43,29,C.navy,true);txt(s,body,150,y+46,width,70,25,C.muted);}
let s=slide('Our project','Opening, 35 seconds. ORION is a local academic application for credit decision support. All data and model outcomes in this deck come from synthetic educational data. Source: README.md, docs/ARCHITECTURE.md, docs/KNOWN_LIMITATIONS.md.','PROJECT',true);
txt(s,'ORION',64,196,1110,112,94,C.white,true);
txt(s,'Enterprise Credit Intelligence\n& Underwriting',68,337,1080,133,49,C.white,true);
txt(s,'An analyst workbench with explainable models\nand recorded human decisions',68,520,1050,88,29,'#bdc9e6');

s=slide('Our project in action','45 seconds. Screenshot is the actual ORION Command Center captured during local browser verification. Crop retains the top command-center view. All borrowers and financial values are fictional. Source: docs/screenshots/command-center.png, backend/main.py, frontend source. The sixteen navigation workspaces are preserved from the supplied screenshot reference.','PROJECT');
const b=await fs.readFile(ROOT+'/docs/screenshots/command-center.png');s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/png',alt:'Actual ORION Command Center, fictional demo records',fit:'contain',crop:{left:0,top:0,right:0,bottom:0.54},position:{left:64,top:183,width:800,height:427}});
txt(s,'16 workspaces',902,189,307,56,35,C.blue,true);txt(s,'One persistent case',902,260,307,44,26,C.navy,true);txt(s,'Intake and documents\n\nAssessment and SHAP\n\nHuman review\n\nCredit memo and audit',902,318,310,280,25,C.ink);
txt(s,'Local FastAPI application with a React interface and Python analytics',64,621,1150,34,23,C.muted);

s=slide('Business opportunity','60 seconds. These workflow problems and benefits are product hypotheses inferred from the supplied project scope, not market research. Initial proposed route is an internal analyst pilot. Measure handling time, correction rate and review consistency against an observed manual baseline before commercial adoption. Source: project directive, docs/PRESENTATION_AND_DEMO.md.','BUSINESS');
txt(s,'Manual credit review',64,186,530,50,32,C.navy,true);txt(s,'ORION opportunity',676,186,540,50,32,C.blue,true);
const pairs=[['Repeated reconciliation','A case joins borrower inputs and reviewed documents'],['Calculations across spreadsheets','Python applies the same capacity and loss formulas'],['Decision rationale spread across files','Saved assessments, review reasons and audit history']];
pairs.forEach((r,i)=>{const y=259+i*115;line(s,64,y-14,1152,0);txt(s,r[0],64,y,520,75,27,C.ink,true);txt(s,r[1],676,y,535,87,26,C.ink);});
txt(s,'Pilot measure: analyst minutes per completed case and corrections per case',64,626,1150,38,23,C.teal,true);

s=slide('Target audience','50 seconds. These are intended user personas, not existing commercial customers. An internal lending team is the proposed initial audience. Analyst begins the case, committee records the final outcome and risk leadership reviews portfolio scenarios. Source: implemented role permissions and docs/PRESENTATION_AND_DEMO.md.','BUSINESS');
const personas=[['Credit analyst','Prepare a reviewable case','Review documents and inputs\nAssess repayment capacity\nExplain the model output'],['Credit committee','Record a defensible decision','Inspect the original assessment\nApprove or override with reasons\nExport the credit memorandum'],['Risk leadership','Review portfolio exposure','Compare stress scenarios\nInspect expected loss\nTrack decisions and overrides']];
personas.forEach((a,i)=>{const x=64+i*398;txt(s,String(i+1).padStart(2,'0'),x,187,350,76,54,C.blue,true);txt(s,a[0],x,285,355,86,32,C.navy,true);txt(s,a[1],x,386,355,73,26,C.teal,true);txt(s,a[2],x,479,355,151,24,C.ink);});

s=slide('Financial ROI','70 seconds. Entire business case is hypothetical, not measured savings or a supplier quote. Assumptions: 1,000 cases/month, INR600 labor value/hour, INR750,000 one-time implementation and INR450,000 first-year operations. Total year-one cost INR1.2m. At 30 minutes saved: 6,000 hours, INR3.6m gross capacity value, INR2.4m net, 200% ROI. Formula: (annual value minus year-one cost)/year-one cost. Ten minutes breaks even. Time released does not automatically create cash savings. Source calculation: scripts/presentation_roi.py and tmp/deck/roi.json.','BUSINESS');
txt(s,'200%',64,182,350,106,79,C.teal,true);txt(s,'Illustrative year-one ROI',64,297,355,76,28,C.navy,true);txt(s,'1,000 cases / month\n30 minutes saved / case\nINR 600 / analyst hour',64,402,355,132,25,C.ink);txt(s,'Capacity value, not realized cash savings',64,559,355,65,23,C.muted);
chart(s,['10 min','20 min','30 min'],[{name:'Annual labor value',values:roi.scenarios.map(r=>r.gross/100000),fill:C.blue},{name:'Year-one cost',values:roi.scenarios.map(()=>roi.cost/100000),fill:'#b7c2d7'}],{x:452,y:180,w:764,h:350,fmt:'0',legend:true});
txt(s,'Sensitivity by minutes saved per case · INR lakh',470,544,740,42,22,C.muted);txt(s,'Base case: INR 36 lakh value − INR 12 lakh cost = INR 24 lakh net',452,590,760,63,25,C.navy,true);

s=slide('System architecture diagram','80 seconds. Editable diagram of implemented local components. UI sends requests to FastAPI. Session authorization and roles protect operations. Python services handle finance, documents and ML. SQLAlchemy persists records and audit events in SQLite. Trusted local versioned model artifacts feed inference. Extraction supports text PDF/TXT, scanned OCR requires optional Tesseract. No live bureau or external LLM exists. Source: backend/main.py, backend/database.py, backend/finance.py, backend/documents.py, src/model.py, docs/ARCHITECTURE.md.');
function node(s,label,sub,x,y,w,h,fill=C.white){rect(s,x,y,w,h,fill,C.line);txt(s,label,x+19,y+18,w-38,42,28,C.navy,true);txt(s,sub,x+19,y+65,w-38,h-70,23,C.muted);}
node(s,'React + TypeScript','Intake, underwriting, portfolio and review',64,190,330,150);
node(s,'FastAPI','Sessions, roles and input validation',475,190,330,150,'#e7e9fc');
node(s,'Case database','SQLite / SQLAlchemy\nCase history and audit',886,190,330,150);
line(s,394,265,81,0,C.blue);line(s,805,265,81,0,C.blue);line(s,640,340,0,57,C.blue);line(s,234,397,812,0,C.blue);line(s,234,397,0,38,C.blue);line(s,640,397,0,38,C.blue);line(s,1046,397,0,38,C.blue);
node(s,'Financial engine','EMI, DTI / DSCR, loss and scenarios',64,435,330,151);
node(s,'ML service','Versioned models and real SHAP values',475,435,330,151);
node(s,'Document service','Uploads, text extraction and field review',886,435,330,151);
txt(s,'Local implementation • No live bureau connection • No external LLM',64,621,1152,38,23,C.muted);

s=slide('Feature selection logic','65 seconds. Six features are defined explicitly by the synthetic generator and inference schema. This is domain mapping, not empirical feature selection on real bank outcomes. Personal burden maps monthly obligations and proposed EMI to income. Business burden maps annual debt service to annual cash flow. Score, utilization and delinquency values require reviewed input. No demographic fairness conclusion is supported. Collateral affects LGD, not the PD vector. Sources: src/data.py, src/model.py, backend/finance.py.');
table(s,[['Feature','Reason for inclusion','Input interpretation'],['Credit score','Credit history signal','Reviewed score'],['Repayment burden','Ability to service debt','Debt service / income or cash flow'],['Delinquencies','Prior payment difficulty','Count of reported events'],['Utilization','Use of available credit','Ratio from 0 to 1'],['Stability years','Employment or business continuity','Non-negative years'],['Business flag','Borrower-type mapping','Personal = 0, business = 1']],{y:175,h:399,widths:[280,435,437]});
txt(s,'Six predefined inputs. No empirical feature-importance or fairness claim.',64,597,1152,55,25,C.teal,true);

s=slide('Model optimization','70 seconds. Training uses 1,440 synthetic rows. GridSearchCV evaluates five stratified folds by ROC-AUC. Logistic scaling remains inside each training fold pipeline. C is inverse L2 regularization strength. Tree models use 100 estimators. Winner is selected by mean training CV AUC. Test results are not used to choose the winner. Source: src/model.py and docs/MODEL_EVALUATION.json.');
table(s,[['Candidate','Search space','Selected configuration'],['Logistic Regression','C: 0.1, 1, 10','C = 1 with StandardScaler'],['Random Forest','Depth: 4, 8\nMin. leaf: 5, 15','Depth = 8, min. leaf = 5'],['XGBoost','Depth: 2, 4\nLearning rate: 0.05, 0.1','Depth = 2, learning rate = 0.05']],{y:181,h:302,widths:[305,417,430]});
txt(s,'1,800 synthetic rows',64,525,370,45,29,C.navy,true);txt(s,'80% training',483,525,340,45,29,C.blue,true);txt(s,'20% test',903,525,310,45,29,C.teal,true);txt(s,'Stratified split, seed 42. Five training folds. Test set held aside during tuning.',64,597,1152,57,25,C.muted);

s=slide('Cross-validation results','70 seconds. All values are measured on synthetic training data. Five-fold mean ROC-AUC and one standard deviation: Logistic 0.867473 +/- 0.013360, Random Forest 0.854464 +/- 0.010095, XGBoost 0.855240 +/- 0.011568. These overlapping fold dispersions do not establish statistically significant superiority. Logistic selected by best mean CV AUC. Generator uses an additive logistic outcome mechanism, which may favor Logistic Regression. Source: docs/MODEL_EVALUATION.json and src/data.py.');
chart(s,m.candidates.map(c=>c.name),[{name:'Mean CV ROC-AUC',values:m.candidates.map(c=>Number(c.cv_auc.toFixed(3))),fill:C.blue}],{x:64,y:187,w:790,h:363,legend:false});
txt(s,'Selected',900,191,310,43,25,C.muted);txt(s,'Logistic\nRegression',900,244,310,112,39,C.navy,true);txt(s,'0.867 ± 0.013',900,390,310,62,32,C.teal,true);txt(s,'Highest mean CV AUC\nFold dispersion overlaps',900,471,310,96,24,C.muted);
txt(s,'Mean ± fold standard deviation: LR 0.867 ± 0.013   RF 0.854 ± 0.010   XGB 0.855 ± 0.012',64,593,1152,58,23,C.ink);

s=slide('Validation on 360 held-out cases','60 seconds. Executed synthetic test metrics for tuned candidates. ROC-AUC and PR-AUC are ranking metrics, F1 is threshold-dependent and Brier is squared probability error, lower is better. Threshold 0.30. Logistic is CV-selected, RF achieves higher F1 on this test set. Do not change model selection based on this test comparison. This random synthetic split gives no out-of-time or real lending validation. Source: docs/MODEL_EVALUATION.json.');
table(s,[['Model','ROC-AUC','PR-AUC','F1','Brier ↓'],...m.candidates.map(c=>[c.name,c.roc_auc.toFixed(3),c.pr_auc.toFixed(3),c.f1.toFixed(3),c.brier.toFixed(3)])],{y:191,h:274,widths:[352,200,200,200,200]});
txt(s,'Logistic Regression',64,517,500,43,31,C.blue,true);txt(s,'Best test ranking and lowest Brier among these candidates',64,569,535,76,25,C.ink);txt(s,'Random Forest',676,517,530,43,31,C.teal,true);txt(s,'Highest F1 at the fixed 0.30 classification threshold',676,569,535,76,25,C.ink);

s=slide('Error analysis','80 seconds. Threshold 0.30 labels a case as default when model probability is at least 0.30. Selected logistic confusion matrix actual rows non-default/default, predicted columns non-default/default: 119,77;19,145. Test data has 196 non-default and164 default cases. FP77 could burden good applicants, FN19 could miss defaults. LR precision65.3%, recall88.4%. RF has FP73 FN14. Outcome costs and policy constraints are needed for threshold optimization on validation data, followed by a fresh independent test. Source: docs/MODEL_EVALUATION.json.');
chart(s,['Logistic','Random Forest','XGBoost'],[{name:'False positives',values:m.candidates.map(c=>c.errors.false_positive),fill:C.blue},{name:'False negatives',values:m.candidates.map(c=>c.errors.false_negative),fill:C.orange}],{x:64,y:185,w:700,h:370,fmt:'0'});
table(s,[['Logistic at 0.30','Pred. 0','Pred. 1'],['Actual 0','119','77'],['Actual 1','19','145']],{x:806,y:191,w:410,h:200,widths:[170,120,120]});
txt(s,'0 = non-default, 1 = default',806,407,410,40,22,C.muted);
txt(s,'88.4% recall',806,455,410,53,33,C.teal,true);txt(s,'65.3% precision',806,513,410,45,27,C.ink);txt(s,'False positives can restrict credit. False negatives can miss defaults.',64,593,1152,43,27,C.navy,true);txt(s,'The threshold remains educational until real outcome costs are available.',64,634,1152,32,22,C.muted);

s=slide('Explainability and human decisions','65 seconds. Actual SHAP contributions explain the stored model output. Logistic and XGBoost use log-odds output, Random Forest probability. Additivity tests exist for all three. Financial decisions separately assess personal DTI/business DSCR and EL=PD*LGD*EAD. Collateral adjusts LGD, not PD. Reviewers can override and must record reasons. Original model assessments remain saved. Mutations create audit events. Sources: src/model.py, backend/finance.py, backend/main.py, tests/test_orion.py.');
row(s,'01','Model assessment','Versioned probability estimate with feature-level SHAP contributions',186);
row(s,'02','Financial and policy review','Python capacity checks and expected loss using explicit LGD assumptions',328);
row(s,'03','Human decision','Reviewer records a rationale. The original model assessment remains saved.',470);
txt(s,'Audit history connects the case, model assessment and final decision',150,617,1040,38,24,C.teal,true);

s=slide('Live demonstration','90 seconds. Suggested flow: create or open a fictional borrower, review uploaded text-document fields, assess the application, inspect SHAP and finance, record a decision and show audit/credit memo. Pre-stage a business case for the scenario if time allows. Do not claim a live bureau call. Server was stopped on user request and must be started deliberately before presenting. Source: docs/PRESENTATION_AND_DEMO.md.','DEMO');
const steps=[['Borrower and documents','Review the fictional borrower\nand extracted inputs'],['Underwriting','Compare repayment capacity, PD\nand expected loss'],['Explain and decide','Inspect SHAP, then save a\nreasoned human decision'],['Memo and scenarios','Open the memo, audit history\nand a business stress case']];
steps.forEach((r,i)=>{const y=184+i*109;txt(s,String(i+1).padStart(2,'0'),64,y,80,52,40,C.blue,true);txt(s,r[0],167,y,435,55,29,C.navy,true);txt(s,r[1],631,y+4,584,78,26,C.ink);line(s,167,y+90,1049,0);});

s=slide('Next steps and boundaries','45 seconds. All model results use synthetic educational data, no real bank default outcomes. No production lending approval or regulatory certification claimed. Proposed next steps: authorized historical outcomes, out-of-time validation, empirical threshold costs, calibration and fairness analysis, document depth and production operational security. Scanned OCR needs Tesseract. Initial strategy is a supervised internal pilot with handling-time measurements. Source: docs/KNOWN_LIMITATIONS.md, docs/MODEL_EVALUATION.json and docs/TEST_REPORT.md.','CLOSING',true);
txt(s,'Working today',64,193,520,54,33,C.white,true);txt(s,'Persistent case workflow\n\nThree trained model families\n\nSHAP, finance and human review\n\nMemo exports and audit history',64,281,520,300,28,'#c7d2ea');
txt(s,'Before a real lending pilot',684,193,532,80,33,C.white,true);txt(s,'Authorized historical outcomes\n\nValidation across time and groups\n\nThreshold and calibration study\n\nOperational security and monitoring',684,281,532,300,28,'#c7d2ea');
txt(s,'Synthetic results demonstrate the system. Real lending requires independent evidence.',64,614,1152,43,25,'#b4c5ef');

await fs.mkdir(ROOT+'/tmp/deck/v2-render',{recursive:true});
await(await PresentationFile.exportPptx(p)).save(ROOT+'/tmp/deck/candidate-v2.pptx');
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:ROOT+'/tmp/deck/candidate-v2.pptx',finalPath:ROOT+'/output/presentation/ORION_Project_Presentation_Final.pptx',pythonExecutable:'C:/Users/Aayush/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:tables,requiredNativeChartOwnerSlides:charts,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:ROOT+'/tmp/deck/validation-final.json'});
console.log(JSON.stringify({slides:p.slides.items.length,result}));
const final=await PresentationFile.importPptx(await FileBlob.load(ROOT+'/output/presentation/ORION_Project_Presentation_Final.pptx'));
for(let i=0;i<final.slides.items.length;i++){const b=await final.export({slide:final.slides.items[i],format:'png',scale:1});await fs.writeFile(ROOT+`/tmp/deck/v2-render/slide-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));}
console.log('Final file rendered: '+final.slides.items.length+' slides');



