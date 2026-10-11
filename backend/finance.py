"""All currency inputs INR. Monthly personal cash flow; annual business accounts."""
import math
import numpy as np

def emi(amount, annual_rate, months):
    if amount < 0 or annual_rate < 0 or months <= 0: raise ValueError('Invalid loan parameters')
    r = annual_rate / 1200
    return amount / months if r == 0 else amount * r / (-math.expm1(-months * math.log1p(r)))

def ratio(a,b): return a/b if b > 0 else None

def financials(kind, p, amount, rate, months):
    payment = emi(amount,rate,months)
    income, debt = p.get('income',0), p.get('obligations',0)
    revenue, ebitda = p.get('revenue',0), p.get('ebitda',0)
    dscr = ratio(p.get('cash_flow',0),p.get('annual_debt_service',0)+payment*12)
    return dict(emi=payment, dti=ratio(debt+payment,income), dscr=dscr,
        interest_coverage=ratio(ebitda,p.get('interest_expense',0)+amount*rate/100),
        current_ratio=ratio(p.get('current_assets',0),p.get('current_liabilities',0)),
        leverage=ratio(p.get('total_debt',0)+amount,p.get('equity',0)),
        ebitda_margin=ratio(ebitda,revenue), net_margin=ratio(p.get('net_profit',0),revenue),
        working_capital=p.get('current_assets',0)-p.get('current_liabilities',0),
        disposable_income=income-debt-payment if kind=='personal' else None)

def feature_values(kind,p,f):
    # Common, explicit cross-product feature schema. Business repayment burden is debt service/cash flow.
    burden = f['dti'] if kind=='personal' else (1/f['dscr'] if f['dscr'] and f['dscr']>0 else 3)
    return [p.get('credit_score',650), min(burden if burden is not None else 3, 4), p.get('delinquencies',0), p.get('utilization',0.3), p.get('stability_years',3), int(kind=='business')]

def assessment(kind,p,amount,rate,months,secured,assets,predict):
    f = financials(kind,p,amount,rate,months)
    prediction = predict(feature_values(kind,p,f))
    pd = prediction['pd']
    recovery = sum(a['value']*(1-a['haircut']) for a in assets) if secured else 0
    lgd = max(0.05,1-min(recovery/amount,0.95)) if secured and assets else 0.65
    reasons=[]
    if kind=='personal' and (f['dti'] is None or f['dti']>0.5): reasons.append('Monthly debt burden exceeds 50% of income')
    if kind=='business' and (f['dscr'] is None or f['dscr']<1.2): reasons.append('Debt service coverage below 1.20x')
    if secured and not assets: reasons.append('Secured facility requires reviewed collateral')
    if p.get('credit_score',650)<600: reasons.append('Reported credit score below 600')
    if kind=='business' and p.get('management_quality',50)<30:reasons.append('Reviewer management-quality score below 30/100; qualitative review required')
    if pd>0.30: reasons.append('Illustrative model default probability exceeds 30%')
    recommendation='declined' if pd>0.55 else 'review' if reasons else 'approved'
    return dict(**f,**prediction,lgd=lgd,ead=amount,expected_loss=pd*lgd*amount,recovery=recovery,
        ltv=ratio(amount,sum(a['value'] for a in assets)) if assets else None,
        recommendation=recommendation,reasons=reasons or ['Capacity and model thresholds satisfied'],
        risk_band='High' if pd>0.30 else 'Moderate' if pd>0.12 else 'Low',
        assumptions='Synthetic ML PD; illustrative 65% unsecured LGD, collateral-adjusted LGD floor 5%; EAD equals requested principal. Not regulatory capital.')

def stress_profile(p,income_shock=0,revenue_shock=0,expense_shock=0):
    out=dict(p)
    out['income']=p.get('income',0)*(1+income_shock/100)
    revenue=p.get('revenue',0)
    costs=revenue-p.get('ebitda',0)
    out['revenue']=revenue*(1+revenue_shock/100)
    out['ebitda']=out['revenue']-costs*(1+expense_shock/100)
    out['cash_flow']=p.get('cash_flow',0)+out['ebitda']-p.get('ebitda',0)
    return out

def monte_carlo(items,iterations=2000,correlation=0.25,seed=42):
    rng=np.random.default_rng(seed)
    common=rng.standard_normal((iterations,1))
    idiosyncratic=rng.standard_normal((iterations,len(items)))
    from scipy.special import ndtri
    latent=np.sqrt(correlation)*common+np.sqrt(1-correlation)*idiosyncratic
    losses=((latent<ndtri(np.clip([x['pd'] for x in items],1e-6,1-1e-6)))*np.array([x['lgd']*x['ead'] for x in items])).sum(axis=1)
    var=float(np.quantile(losses,.95)); tail=losses[losses>=var]
    counts,edges=np.histogram(losses,bins=12)
    return dict(mean=float(losses.mean()),var95=var,cvar95=float(tail.mean()),iterations=iterations,seed=seed,histogram=[{'loss':float(edges[i]),'count':int(v)} for i,v in enumerate(counts)])
