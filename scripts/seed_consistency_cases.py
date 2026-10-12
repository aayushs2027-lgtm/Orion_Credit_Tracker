"""Add two clearly synthetic, idempotent evidence-review demonstrations via the audited API."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.main import app

def seed():
    password=next(x.split('=',1)[1].strip() for x in Path('.env').read_text().splitlines() if x.startswith('ORION_ADMIN_PASSWORD='))
    with TestClient(app) as client:
        assert client.post('/api/login',json={'username':'admin','password':password}).status_code==200
        for kind,name,identity in [('personal','Synthetic Demo · Address Reconciliation','SYNTHETIC-ADDRESS-001'),('business','Synthetic Demo · Rapid Revenue Growth','SYNTHETIC-REVENUE-001')]:
            if client.get('/api/customers',params={'q':identity}).json()['total']:continue
            financial=dict(income=150000,obligations=10000,credit_score=760,revenue=50000000,ebitda=8000000,cash_flow=6000000,annual_debt_service=1000000)
            if kind=='business':financial.update(previous_year_revenue=10000000,previous_revenue_year=2024,revenue_year=2025)
            r=client.post('/api/customers',json=dict(kind=kind,name=name,identity=identity,address='12 Synthetic Lake Road, Pune',sector='Synthetic Demonstration',financial=financial));assert r.status_code==200,r.text
            r=client.post('/api/applications',json=dict(customer_id=r.json()['id'],amount=500000 if kind=='personal' else 5000000,rate=12,months=60));assert r.status_code==200,r.text
            aid=r.json()['id']
            documents=[('synthetic-identity.txt','SYNTHETIC DEMONSTRATION — No Real Customer\nAddress: 12 Synthetic Lake Road, Pune'),('synthetic-bank-statement.txt','SYNTHETIC DEMONSTRATION — No Real Customer\nAddress: 88 Synthetic Garden Lane, Mumbai'),('synthetic-employer-record.txt','SYNTHETIC DEMONSTRATION — No Real Customer\nAddress: 31 Synthetic Hill Street, Bengaluru')] if kind=='personal' else [('synthetic-annual-revenue.txt','SYNTHETIC DEMONSTRATION — No Real Business\n2024 Annual Revenue: INR 10,000,000\n2025 Annual Revenue: INR 50,000,000\nA 400% increase requires documentary verification. No fraud conclusion is implied.')]
            for filename,text in documents:
                r=client.post(f'/api/applications/{aid}/documents',files={'file':(filename,text.encode(),'text/plain')});assert r.status_code==200,r.text
            for document in client.get(f'/api/applications/{aid}').json()['documents']:
                for field in document['fields']:
                    if field['key']=='address':
                        r=client.patch(f"/api/fields/{field['id']}",json={'value':field['value'],'status':'accepted'});assert r.status_code==200,r.text
            r=client.post(f'/api/applications/{aid}/assess');assert r.status_code==200,r.text
            print(f'Added {name}: APP-{aid}')
if __name__=='__main__':seed()
