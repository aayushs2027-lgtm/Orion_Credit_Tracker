import os,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['ORION_DATABASE_URL']='sqlite:///data/test-'+uuid.uuid4().hex+'.db'
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from backend.database import Base,engine,Session,User,Assessment,Audit,Profile
from backend.security import password_hash,verify
from backend.main import app
from backend.finance import emi,financials,monte_carlo,assessment,stress_profile
from src.model import metadata,predict

@pytest.fixture(scope='module')
def client():
    Base.metadata.create_all(engine)
    with Session() as db:
        for name,role in [('admin','admin'),('analyst','analyst'),('viewer','viewer')]:db.add(User(username=name,password=password_hash('TestPassword123!'),role=role))
        db.commit()
    with TestClient(app) as c:
        assert c.post('/api/login',json={'username':'admin','password':'TestPassword123!'}).status_code==200
        yield c
    engine.dispose()
    Path(engine.url.database).unlink(missing_ok=True)

def test_finance_known_values():
    assert emi(100000,0,10)==10000
    assert emi(1000000,12,60)==pytest.approx(22244.44785,rel=1e-7)
    with pytest.raises(ValueError):emi(1,1,0)
    f=financials('business',dict(cash_flow=120000,annual_debt_service=10000,ebitda=50000,interest_expense=5000,current_assets=60000,current_liabilities=30000,total_debt=10000,equity=20000,revenue=200000,net_profit=10000),100000,0,60)
    assert f['dscr']==4
    assert f['current_ratio']==2
    assert f['leverage']==5.5
    assert financials('personal',{},100,0,10)['dti'] is None

def test_unsecured_not_declined_for_collateral():
    r=assessment('personal',dict(income=100000,obligations=0,credit_score=800),100000,10,36,False,[],lambda _:dict(pd=.05))
    assert r['recommendation']=='approved'
    assert r['lgd']==.65
    assert r['expected_loss']==3250

def test_simulation_reproducible_and_stress():
    items=[dict(pd=.2,lgd=.6,ead=100000),dict(pd=.1,lgd=.5,ead=50000)]
    a=monte_carlo(items,2000,.3)
    assert a==monte_carlo(items,2000,.3)
    assert a['cvar95']>=a['var95']>=a['mean']
    p=stress_profile(dict(income=100,revenue=1000,ebitda=200,cash_flow=150),-20,-10,10)
    assert p['income']==80
    assert p['ebitda']==pytest.approx(20)

def create_case(client,kind='personal',secured=False):
    data=dict(kind=kind,name='Test Borrower '+uuid.uuid4().hex[:6],identity=uuid.uuid4().hex,address='Fictional test address',financial=dict(income=150000,obligations=10000,credit_score=760,revenue=24000000,ebitda=4000000,cash_flow=3200000,annual_debt_service=500000))
    c=client.post('/api/customers',json=data);assert c.status_code==200,c.text
    cid=c.json()['id'];data['identity']=c.json()['identity']
    a=client.post('/api/applications',json=dict(customer_id=cid,amount=500000,rate=12,months=60,secured=secured));assert a.status_code==200,a.text
    return cid,a.json()['id'],data

def test_multiple_document_addresses_and_manager_gate(client):
    cid,aid,data=create_case(client)
    for name,address in [('identity.txt','10 Synthetic Oak Road'),('bank.txt','88 Synthetic Pine Lane')]:
        assert client.post(f'/api/applications/{aid}/documents',files={'file':(name,('Address: '+address).encode(),'text/plain')}).status_code==200
    detail=client.get(f'/api/applications/{aid}').json()
    for document in detail['documents']:
        for field in document['fields']:
            for _ in range(2):
                assert client.patch(f"/api/fields/{field['id']}",json={'value':field['value'],'status':'accepted'}).status_code==200
    flags=[f for f in client.get('/api/flags').json() if f['customer_id']==cid]
    assert len(flags)==2  # Re-review is idempotent; each conflicting source retains provenance.
    assert all('page 1' in f['detail'] and 'Reviewed source:' in f['detail'] for f in flags)
    assert client.get(f'/api/customers/{cid}').json()['address']==data['address']
    assert client.post(f'/api/applications/{aid}/assess').status_code==200
    decision={'decision':'approved','reason':'Synthetic documents checked by manager','override':True}
    assert client.post(f'/api/applications/{aid}/review',json=decision).status_code==409
    for flag in flags:
        url=f"/api/flags/{flag['id']}"
        assert client.patch(url,json={'status':'manager_approved','reason':'Manager tried before verification'}).status_code==409
        assert client.patch(url,json={'status':'dismissed','reason':'Attempt to bypass verification gate'}).status_code==422
        assert client.patch(url,json={'status':'escalated','reason':'Send to identity verification team'}).status_code==422
        assert client.patch(url,json={'status':'escalated','assigned_team':'Identity Verification','reason':'Compare the address on bank and identity evidence'}).status_code==200
        assert client.patch(url,json={'status':'verified','reason':' '*12}).status_code==422
        outstanding=sum(f['status'] not in ('resolved','dismissed','manager_approved') for f in client.get('/api/flags').json())
        assert client.get('/api/portfolio').json()['flags']==outstanding
        assert client.patch(url,json={'status':'verified','reason':'Reviewed dated documents and confirmed a residential move'}).status_code==200
        client.post('/api/login',json={'username':'analyst','password':'TestPassword123!'})
        assert client.patch(url,json={'status':'manager_approved','reason':'Analyst attempting manager approval'}).status_code==403
        client.post('/api/login',json={'username':'admin','password':'TestPassword123!'})
        assert client.patch(url,json={'status':'manager_approved','reason':'Manager reviewed evidence and accepts documented move'}).status_code==200
        assert client.patch(url,json={'status':'investigating','reason':'Try reopening a locked manager decision'}).status_code==409
    before=client.get(f'/api/applications/{aid}').json()['assessment']
    assert client.post(f'/api/applications/{aid}/review',json=decision).status_code==200
    assert client.get(f'/api/applications/{aid}').json()['assessment']==before

@pytest.mark.parametrize('previous,current,expected',[(1000000,5000000,True),(1000000,2999999,False),(1000000,3000000,True),(0,1000000,True),(0,0,False)])
def test_revenue_growth_comparison(client,previous,current,expected):
    cid,aid,data=create_case(client,'business')
    data['financial'].update(revenue=current,previous_year_revenue=previous,previous_revenue_year=2024,revenue_year=2025)
    for _ in range(2):assert client.patch(f'/api/customers/{cid}',json=data).status_code==200
    flags=[f for f in client.get('/api/flags').json() if f['customer_id']==cid and f['category']=='revenue_growth']
    assert len(flags)==int(expected)
    if expected:
        assert '2024' in flags[0]['detail'] and '2025' in flags[0]['detail']
        if previous==0:assert 'undefined' in flags[0]['detail']
    data['financial']['previous_revenue_year']=2022
    assert client.patch(f'/api/customers/{cid}',json=data).status_code==422

def test_address_formatting_is_not_a_conflict(client):
    cid,aid,data=create_case(client)
    client.post(f'/api/applications/{aid}/documents',files={'file':('same.txt',b'Address: FICTIONAL, TEST ADDRESS','text/plain')})
    f=client.get(f'/api/applications/{aid}').json()['documents'][0]['fields'][0]
    assert client.patch(f"/api/fields/{f['id']}",json={'value':f['value'],'status':'accepted'}).status_code==200
    assert not [f for f in client.get('/api/flags').json() if f['customer_id']==cid]

def test_personal_end_to_end(client):
    cid,aid,data=create_case(client)
    doc=client.post(f'/api/applications/{aid}/documents',files={'file':('report.txt',b'Monthly income: INR 160,000\nCredit score: 780\n','text/plain')})
    assert doc.status_code==200,doc.text
    detail=client.get(f'/api/applications/{aid}').json()
    for f in detail['documents'][0]['fields']:
        assert client.patch('/api/fields/'+str(f['id']),json=dict(value=f['value'],status='accepted')).status_code==200
    assert client.post(f'/api/applications/{aid}/apply-fields').status_code==200
    r=client.post(f'/api/applications/{aid}/assess');assert r.status_code==200,r.text
    result=r.json();assert result['expected_loss']==pytest.approx(result['pd']*result['lgd']*result['ead'])
    assert result['shap'] and result['model_version']
    assert client.post(f'/api/applications/{aid}/review',json=dict(decision='approved',reason='Verified income and capacity',override=True)).status_code==200
    detail=client.get(f'/api/applications/{aid}').json()
    assert detail['status']=='approved';assert detail['reviews'][0]['original']==result['recommendation']
    assert client.post(f'/api/applications/{aid}/assess').status_code==409
    assert client.get(f'/api/applications/{aid}/memo').status_code==200

def test_business_and_collateral(client):
    cid,aid,data=create_case(client,'business',True)
    assert client.post(f'/api/applications/{aid}/collateral',json=dict(category='Property',value=900000,haircut=.25,valuation_date='2026-10-01')).status_code==200
    r=client.post(f'/api/applications/{aid}/assess');assert r.status_code==200,r.text
    result=r.json();assert result['lgd']==pytest.approx(.05);assert result['dscr']>1.2
    stress=client.post(f'/api/applications/{aid}/scenario',json=dict(revenue_shock=-30,expense_shock=10,rate_change=2))
    assert stress.status_code==200,stress.text
    assert stress.json()['stressed']['dscr']<result['dscr']
    assert client.post(f'/api/applications/{aid}/structure').status_code==200
    assert len(client.get(f'/api/applications/{aid}').json()['assessments'])==1

def test_discrepancy_workflow_and_search(client):
    cid,aid,data=create_case(client)
    data['financial']['income']=450000
    data['address']='New Fictional Address'
    assert client.patch(f'/api/customers/{cid}',json=data).status_code==200
    flags=[f for f in client.get('/api/flags').json() if f['customer_id']==cid]
    assert {f['category'] for f in flags}=={'income','address'}
    assert client.patch('/api/flags/'+str(flags[0]['id']),json=dict(status='resolved',reason='Verified supporting evidence')).status_code==200
    assert client.get('/api/customers',params={'q':data['name']}).json()['total']==1
    assert client.get('/api/matches',params={'identity':data['identity']}).json()[0]['match_score']==100
    assert client.post('/api/customers',json=data).status_code==409

def test_security_and_invalid_inputs(client):
    with TestClient(app) as anon:
        assert anon.get('/api/customers').status_code==401
        assert anon.post('/api/login',json=dict(username='viewer',password='TestPassword123!')).status_code==200
        assert anon.post('/api/models/train').status_code==403
        assert anon.post('/api/customers',json=dict(kind='personal',name='Blocked',identity='BLOCKED',address='Test',financial={})).status_code==403
    cid,aid,_=create_case(client)
    assert client.post('/api/applications',json=dict(customer_id=cid,amount=-1,rate=12,months=60)).status_code==422
    assert client.post(f'/api/applications/{aid}/documents',files={'file':('evil.exe',b'xxx')}).status_code==422
    assert client.post(f'/api/applications/{aid}/documents',files={'file':('fake.pdf',b'not pdf')}).status_code==422
    assert client.post(f'/api/applications/{aid}/scenario',json=dict(correlation=2)).status_code==422
    assert client.post('/api/logout',headers={'Origin':'https://evil.example'}).status_code==403

def test_portfolio_audit_and_models(client):
    p=client.get('/api/portfolio').json()
    assert p['exposure']==pytest.approx(sum(x['ead'] for x in p['items']))
    assert p['expected_loss']==pytest.approx(sum(x['expected_loss'] for x in p['items']))
    assert client.post('/api/portfolio/scenario',json={'iterations':500}).status_code==200
    assert client.get('/api/audit').json()['integrity'] is True
    assert client.get('/api/export/audit').status_code==200
    assert client.get('/api/export/portfolio').status_code==200
    m=metadata();assert len(m['candidates'])==3
    for x in m['candidates']:assert 0<=x['roc_auc']<=1 and len(x['confusion'])==2
    a=predict([750,.3,0,.2,5,0]);b=predict([750,.3,0,.2,5,0]);assert a==b
    with Session() as db:
        events=list(db.scalars(select(Audit).order_by(Audit.id)));assert verify(events)
        events[-1].action='tampered';assert not verify(events)

@pytest.mark.parametrize('name',['Logistic Regression','Random Forest','XGBoost'])
def test_each_algorithm_shap_additivity(name):
    import math
    r=predict([750,.3,0,.2,5,0],name)
    total=r['shap_base']+sum(x['value'] for x in r['shap'])
    prob=total if r['shap_units']=='probability' else 1/(1+math.exp(-total))
    assert prob==pytest.approx(r['pd'],abs=1e-5)

def test_report_disbursement_and_governance(client):
    cid,aid,_=create_case(client)
    report=b'Credit score: 780\nInquiries: 2\nAccount: Demo Bank | Personal | 100000 | 200000 | 5000 | 0 | 000000\n'
    r=client.post(f'/api/applications/{aid}/documents',files={'file':('bureau.txt',report,'text/plain')});assert r.status_code==200
    did=r.json()['id']
    for f in client.get(f'/api/applications/{aid}').json()['documents'][0]['fields']:
        assert client.patch('/api/fields/'+str(f['id']),json=dict(value=f['value'],status='accepted')).status_code==200
    r=client.post(f'/api/documents/{did}/credit-report');assert r.status_code==200,r.text
    assert r.json()['accounts'][0]['monthly_payment']==5000
    assert client.post(f'/api/documents/{did}/credit-report').status_code==409
    assert client.post(f'/api/applications/{aid}/disburse',json={'date':'2026-10-01'}).status_code==409
    assert client.post(f'/api/applications/{aid}/assess?algorithm=Random%20Forest').status_code==200
    assert client.post(f'/api/applications/{aid}/review',json=dict(decision='approved',reason='Fictional verified review approval',override=True)).status_code==200
    assert client.post(f'/api/applications/{aid}/disburse',json={'date':'2026-10-01'}).status_code==200
    assert client.post(f'/api/applications/{aid}/repayments',json=dict(date='2026-10-02',amount=10000,principal_paid=8000,days_past_due=0)).json()['outstanding']==492000
    assert client.post(f'/api/applications/{aid}/repayments',json=dict(date='2026-10-02',amount=10000,principal_paid=18000,days_past_due=0)).status_code==422
    m=metadata()
    # Test database registry is independent from demo registry.
    from backend.database import ModelVersion
    with Session() as db:
        db.add(ModelVersion(id=m['version'],metrics=m));db.commit()
    assert client.post('/api/models/'+m['version']+'/validation',json=dict(status='validated',note='Verified educational training and test split')).status_code==200
    assert client.post('/api/users',json=dict(username='test-new',password='NewSecurePass123!',role='viewer')).status_code==200
    assert client.get('/api/customers',params={'q':'CUS-'+str(cid)}).json()['total']==1
    assert client.get('/api/audit').json()['integrity'] is True

def test_pdf_extraction_and_input_corrections(client):
    import pymupdf
    cid,aid,_=create_case(client)
    doc=pymupdf.open();page=doc.new_page();page.insert_text((50,50),'Monthly income: INR 120000\nCredit score: 750')
    r=client.post(f'/api/applications/{aid}/documents',files={'file':('salary.pdf',doc.tobytes(),'application/pdf')});doc.close()
    assert r.status_code==200,r.text
    data=client.get(f'/api/applications/{aid}').json();f=data['documents'][0]['fields'][0]
    assert f['page']==1 and f['evidence']
    assert client.patch('/api/fields/'+str(f['id']),json=dict(value='not a number',status='corrected')).status_code==422
    assert client.patch('/api/fields/'+str(f['id']),json=dict(value='125000',status='corrected')).status_code==200
    assert client.post(f'/api/applications/{aid}/apply-fields').status_code==200
    assert client.get(f'/api/applications/{aid}').json()['financial']['income']==125000

def test_review_permission_and_rollback(client):
    cid,aid,_=create_case(client)
    r=client.post(f'/api/applications/{aid}/assess');assert r.status_code==200
    with TestClient(app) as limited:
        assert limited.post('/api/login',json=dict(username='analyst',password='TestPassword123!')).status_code==200
        assert limited.post(f'/api/applications/{aid}/review',json=dict(decision='approved',reason='Attempt unauthorized approval',override=True)).status_code==403
    a=client.get(f'/api/applications/{aid}').json();assert a['status']=='pending_review' and not a['reviews']
    assert client.get('/api/audit').json()['integrity'] is True
