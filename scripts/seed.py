"""Idempotent fictional demo data and local credentials, never real customer data."""
import os, sys, secrets
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from backend.database import *
from backend.schemas import Financial
from backend.security import password_hash,audit
from backend.finance import assessment
from src.model import metadata,predict,train

def seed():
    with Session() as db:
        if db.scalar(select(User)): print('Seed already exists; unchanged');return
        password=os.getenv('ORION_ADMIN_PASSWORD') or secrets.token_urlsafe(15)
        credential_path=ROOT/'.env'
        if not credential_path.exists():credential_path.write_text('ORION_ADMIN_PASSWORD='+password+'\n',encoding='utf-8')
        for name,role in [('admin','admin'),('reviewer','reviewer'),('analyst','analyst'),('viewer','viewer')]:db.add(User(username=name,role=role,password=password_hash(password)))
        try:m=metadata()
        except RuntimeError:m=train()
        db.add(ModelVersion(id=m['version'],metrics=m))
        names=['Priya Sharma','Arjun Mehta','Rahul Mehta','Dr. Neha Verma','Ananya Deshmukh','Vikram Singh Gupta','Crestive Media Works Ltd','ABC Industrial Components Pvt Ltd','Nova Retail Solutions Pvt Ltd','Zenith Logistics Pvt Ltd']
        for i,name in enumerate(names):
            kind='personal' if i<6 else 'business'
            c=Customer(kind=kind,name=name,identity=f'DEMO-KYC-{i+1:03}',email=f'fictional{i+1}@example.test',address='12 Example Road, Mumbai' if i in (1,4) else f'{i+1} Fictional Avenue, Mumbai',phone='9000000001' if i in (1,4) else f'90000000{i+10}',sector=['Retail','Technology','Healthcare','Manufacturing'][i%4]);db.add(c);db.flush()
            p=Financial(income=[240000,80000,30000,350000,90000,150000][i%6],obligations=10000 if i!=2 else 20000,credit_score=[790,620,480,810,670,740][i%6],delinquencies=3 if i==2 else 0,stability_years=4+i,revenue=24000000,ebitda=4000000 if i!=8 else 800000,cash_flow=3200000 if i!=8 else 500000,annual_debt_service=800000,interest_expense=250000,current_assets=6000000,current_liabilities=3000000,total_debt=5000000,equity=8000000,net_profit=2000000).model_dump()
            if i==1:
                db.add(Profile(customer_id=c.id,values=dict(p,income=25000)));db.add(Flag(customer_id=c.id,category='income',detail='Reported income increased 3.20x from INR 25,000 to INR 80,000. Requires verification.'))
            if i==4:db.add(Flag(customer_id=c.id,category='address',detail='Current Mumbai address differs from previous Pune address. Requires verification.'))
            db.add(Profile(customer_id=c.id,values=p))
            secured=i in (4,7,9);amount=1800000 if kind=='personal' else 5000000
            a=Application(customer_id=c.id,amount=amount,rate=12 if kind=='personal' else 11,months=60,secured=int(secured),status='pending_review');db.add(a);db.flush()
            aa=[]
            if secured:
                asset=Collateral(application_id=a.id,category='Property',value=amount*1.6,haircut=.25,valuation_date='2026-10-01');db.add(asset);aa=[dict(value=asset.value,haircut=asset.haircut)]
            result=assessment(kind,p,amount,a.rate,a.months,secured,aa,predict);ar=Assessment(application_id=a.id,model_version=m['version'],result=result);db.add(ar);db.flush()
            if i in (0,3):
                a.status='approved';db.add(Review(application_id=a.id,assessment_id=ar.id,reviewer='admin',original=result['recommendation'],decision='approved',reason='Fictional seed credit committee review with verified capacity',override=int(result['recommendation']!='approved')))
            if i==2:a.status='declined'
            if i==5:
                # Explicitly exercise a contrary human decision, preserving the assessment.
                a.status='declined' if result['recommendation']!='declined' else 'approved'
                db.add(Review(application_id=a.id,assessment_id=ar.id,reviewer='admin',original=result['recommendation'],decision=a.status,reason='Fictional committee override after additional verification and risk appetite review',override=1))
            if i==0:
                db.add(Loan(application_id=a.id,principal=amount,outstanding=amount-30000,disbursed_date='2026-08-01'))
                db.add(Repayment(application_id=a.id,date='2026-09-01',amount=40000,days_past_due=0))
            audit(db,'seed','fictional.application.created',str(a.id),{'synthetic':True})
        db.add(Relationship(customer_id=7,related_id=5,relation='director'))
        audit(db,'seed','seed.completed','demo',{'customers':10,'fictional':True});db.commit()
        print('Fictional demo created. Usernames: admin, reviewer, analyst, viewer. Password saved locally in .env (not logged).')
if __name__=='__main__':seed()
