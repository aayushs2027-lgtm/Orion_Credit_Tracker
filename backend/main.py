import csv, io, json, os, secrets, time
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, or_, func
from sqlalchemy.exc import IntegrityError
from .database import *
from .schemas import *
from .database import Field
from .security import password_matches, password_hash, audit, verify
from .finance import assessment, stress_profile, monte_carlo, emi
from .documents import extract, credit_accounts
from src.model import predict, metadata, train

app=FastAPI(title='ORION Credit Intelligence',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://127.0.0.1:5173','http://localhost:5173'],allow_credentials=True,allow_methods=['GET','POST','PATCH','DELETE'],allow_headers=['Content-Type','Authorization'])
def db_session():
    with Session() as db:
        try: yield db; db.commit()
        except Exception: db.rollback(); raise
def user(request:Request,db=Depends(db_session)):
    raw=request.cookies.get('orion_session','')
    token=db.get(Token,__import__('hashlib').sha256(raw.encode()).hexdigest())
    if not token or token.expires<time.time(): raise HTTPException(401,'Sign in required')
    return db.get(User,token.user_id)
def analyst(u=Depends(user)):
    if u.role not in ('analyst','reviewer','admin'): raise HTTPException(403,'Analyst role required')
    return u
def reviewer(u=Depends(user)):
    if u.role not in ('reviewer','admin'): raise HTTPException(403,'Reviewer role required')
    return u
def admin(u=Depends(user)):
    if u.role!='admin': raise HTTPException(403,'Administrator role required')
    return u
@app.middleware('http')
async def protection(request,call_next):
    if request.method in ('POST','PATCH','DELETE'):
        origin=request.headers.get('origin')
        if origin and origin not in ('http://127.0.0.1:5173','http://localhost:5173','http://127.0.0.1:8000','http://localhost:8000'): return Response('Untrusted origin',403)
        if int(request.headers.get('content-length','0'))>11*1024*1024: return Response('Upload limit exceeded',413)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    return response
def get(db,cls,id):
    obj=db.get(cls,id)
    if not obj: raise HTTPException(404,f'{cls.__name__} not found')
    return obj
def row(obj): return {c.name:getattr(obj,c.name) for c in obj.__table__.columns}
def latest(db,cls,field,id): return db.scalar(select(cls).where(field==id).order_by(cls.id.desc()).limit(1))
def profile(db,cid):
    p=latest(db,Profile,Profile.customer_id,cid)
    return p.values if p else Financial().model_dump()
def assets(db,aid): return [row(a) for a in db.scalars(select(Collateral).where(Collateral.application_id==aid))]
def calculate(db,a,scenario=None,algorithm=None):
    c=get(db,Customer,a.customer_id); p=profile(db,c.id); aa=assets(db,a.id); rate=a.rate
    if scenario:
        p=stress_profile(p,scenario.income_shock,scenario.revenue_shock,scenario.expense_shock)
        rate=max(0,rate+scenario.rate_change)
        aa=[dict(x,value=x['value']*(1+scenario.collateral_shock/100)) for x in aa]
    def prediction(values):
        r=predict(values,algorithm)
        if scenario:
            r['model_pd']=r['pd'];r['pd']=min(.999,r['pd']*scenario.pd_multiplier)
            r['scenario_pd_multiplier']=scenario.pd_multiplier
        return r
    result=assessment(c.kind,p,a.amount,rate,a.months,a.secured,aa,prediction)
    return result
def application_row(db,a):
    c=get(db,Customer,a.customer_id); ar=latest(db,Assessment,Assessment.application_id,a.id)
    return dict(**row(a),customer=row(c),assessment=row(ar) if ar else None)

_attempts={}
@app.post('/api/login')
def login(data:Login,response:Response,request:Request,db=Depends(db_session)):
    key=request.client.host if request.client else 'local'; attempts=[t for t in _attempts.get(key,[]) if t>time.time()-60]
    if len(attempts)>=10: raise HTTPException(429,'Too many attempts; wait one minute')
    attempts.append(time.time()); _attempts[key]=attempts
    u=db.scalar(select(User).where(User.username==data.username))
    if not u or not password_matches(data.password,u.password): raise HTTPException(401,'Invalid credentials')
    raw=secrets.token_urlsafe(32); db.add(Token(id=__import__('hashlib').sha256(raw.encode()).hexdigest(),user_id=u.id,expires=time.time()+28800))
    response.set_cookie('orion_session',raw,httponly=True,samesite='strict',max_age=28800)
    audit(db,u.username,'login','session')
    return dict(username=u.username,role=u.role)
@app.get('/api/me')
def me(u=Depends(user)): return dict(username=u.username,role=u.role)
@app.post('/api/logout')
def logout(request:Request,response:Response,u=Depends(user),db=Depends(db_session)):
    token=db.get(Token,__import__('hashlib').sha256(request.cookies.get('orion_session','').encode()).hexdigest())
    if token: db.delete(token)
    response.delete_cookie('orion_session'); return {'ok':True}
@app.get('/api/health')
def health(): return {'status':'ok','synthetic_demo':True}
@app.get('/api/customers')
def customers(q:str='',kind:str='',page:int=1,u=Depends(user),db=Depends(db_session)):
    if page<1: raise HTTPException(422,'Page must be positive')
    stmt=select(Customer)
    if q:
        number=q.upper().replace('APP-','').replace('CUS-','')
        numeric=int(number) if number.isdigit() else -1
        stmt=stmt.where(or_(Customer.name.icontains(q),Customer.identity.icontains(q),Customer.id==numeric if not q.upper().startswith('APP-') else Customer.id==-1,Customer.id.in_(select(Application.customer_id).where(Application.id==numeric)) if not q.upper().startswith('CUS-') else Customer.id==-1))
    if kind: stmt=stmt.where(Customer.kind==kind)
    total=db.scalar(select(func.count()).select_from(stmt.subquery()))
    return dict(items=[dict(**row(c),financial=profile(db,c.id)) for c in db.scalars(stmt.order_by(Customer.id).offset((page-1)*20).limit(20))],total=total,page=page)
@app.post('/api/customers')
def create_customer(data:CustomerInput,u=Depends(analyst),db=Depends(db_session)):
    values=data.model_dump(); financial=values.pop('financial'); values['identity']=values['identity'].upper().strip()
    if db.scalar(select(Customer).where(Customer.identity==values['identity'])): raise HTTPException(409,'Identity already exists; open the existing customer')
    c=Customer(**values); db.add(c); db.flush(); db.add(Profile(customer_id=c.id,values=financial)); audit(db,u.username,'customer.created',str(c.id),{'kind':c.kind})
    return row(c)
@app.get('/api/customers/{cid}')
def customer(cid:int,u=Depends(user),db=Depends(db_session)):
    c=get(db,Customer,cid)
    return dict(**row(c),financial=profile(db,cid),profiles=[row(x) for x in db.scalars(select(Profile).where(Profile.customer_id==cid).order_by(Profile.id.desc()))],applications=[application_row(db,x) for x in db.scalars(select(Application).where(Application.customer_id==cid))],flags=[row(x) for x in db.scalars(select(Flag).where(Flag.customer_id==cid))],relationships=[row(x) for x in db.scalars(select(Relationship).where(Relationship.customer_id==cid))])
@app.patch('/api/customers/{cid}')
def update_customer(cid:int,data:CustomerInput,u=Depends(analyst),db=Depends(db_session)):
    c=get(db,Customer,cid); old=profile(db,cid); vals=data.model_dump(); financial=vals.pop('financial')
    if vals['kind']!=c.kind: raise HTTPException(422,'Customer type cannot change')
    if vals['identity'].upper().strip()!=c.identity: raise HTTPException(422,'Identity cannot change; create an investigation')
    vals['identity']=vals['identity'].upper().strip()
    if old.get('income',0)>0 and financial['income']/old['income']>=2:
        db.add(Flag(customer_id=cid,category='income',detail=f"Income increased {financial['income']/old['income']:.2f}x; {old['income']} to {financial['income']}; verification required"))
    if vals['address']!=c.address: db.add(Flag(customer_id=cid,category='address',detail=f'Address changed from {c.address} to {vals["address"]}'))
    for k,v in vals.items(): setattr(c,k,v)
    db.add(Profile(customer_id=cid,values=financial));audit(db,u.username,'customer.updated',str(cid),{'previous_financial':old,'new_financial':financial})
    return row(c)
@app.post('/api/customers/{cid}/relationships')
def relationship(cid:int,data:RelationshipInput,u=Depends(analyst),db=Depends(db_session)):
    get(db,Customer,cid);get(db,Customer,data.related_id)
    if cid==data.related_id: raise HTTPException(422,'Choose a different customer')
    r=Relationship(customer_id=cid,**data.model_dump());db.add(r);audit(db,u.username,'relationship.created',str(cid),data.model_dump());return {'ok':True}
@app.get('/api/matches')
def matches(name:str='',identity:str='',u=Depends(user),db=Depends(db_session)):
    from rapidfuzz.fuzz import WRatio
    found=[dict(**row(c),match_score=100 if c.identity==identity.upper().strip() else WRatio(name.casefold(),c.name.casefold())) for c in db.scalars(select(Customer))]
    return sorted([x for x in found if x['match_score']>=60],key=lambda x:-x['match_score'])[:10]
@app.get('/api/applications')
def applications(status:str='',u=Depends(user),db=Depends(db_session)):
    stmt=select(Application)
    if status: stmt=stmt.where(Application.status==status)
    return [application_row(db,a) for a in db.scalars(stmt.order_by(Application.id.desc()))]
@app.post('/api/applications')
def create_application(data:ApplicationInput,u=Depends(analyst),db=Depends(db_session)):
    get(db,Customer,data.customer_id);a=Application(**data.model_dump());db.add(a);db.flush();audit(db,u.username,'application.created',str(a.id),data.model_dump());return row(a)
@app.get('/api/applications/{aid}')
def application(aid:int,u=Depends(user),db=Depends(db_session)):
    a=get(db,Application,aid)
    documents=[]
    for d in db.scalars(select(Document).where(Document.application_id==aid)):
        dr=row(d);dr.pop('storage_name');dr['fields']=[row(f) for f in db.scalars(select(Field).where(Field.document_id==d.id))];documents.append(dr)
    reports=[]
    for r in db.scalars(select(CreditReport).where(CreditReport.application_id==aid)):
        reports.append(dict(**row(r),accounts=[row(x) for x in db.scalars(select(CreditAccount).where(CreditAccount.report_id==r.id))]))
    loan=db.scalar(select(Loan).where(Loan.application_id==aid))
    return dict(**application_row(db,a),financial=profile(db,a.customer_id),collateral=assets(db,aid),documents=documents,credit_reports=reports,loan=row(loan) if loan else None,assessments=[row(x) for x in db.scalars(select(Assessment).where(Assessment.application_id==aid))],reviews=[row(x) for x in db.scalars(select(Review).where(Review.application_id==aid))],repayments=[row(x) for x in db.scalars(select(Repayment).where(Repayment.application_id==aid))])
@app.post('/api/applications/{aid}/assess')
def assess(aid:int,algorithm:Literal['Logistic Regression','Random Forest','XGBoost']|None=None,u=Depends(analyst),db=Depends(db_session)):
    a=get(db,Application,aid)
    if a.status in ('approved','declined'): raise HTTPException(409,'Final decision exists; create a new application for reassessment')
    try: result=calculate(db,a,algorithm=algorithm)
    except RuntimeError as e: raise HTTPException(409,str(e))
    r=Assessment(application_id=aid,model_version=result['model_version'],result=result);db.add(r);a.status='pending_review';audit(db,u.username,'assessment.created',str(aid),result);return result
@app.post('/api/applications/{aid}/collateral')
def add_asset(aid:int,data:AssetInput,u=Depends(analyst),db=Depends(db_session)):
    a=get(db,Application,aid)
    if a.status in ('approved','declined'): raise HTTPException(409,'Final application is locked')
    if not a.secured: raise HTTPException(422,'Collateral requires a secured application')
    x=Collateral(application_id=aid,**data.model_dump());db.add(x);audit(db,u.username,'collateral.created',str(aid),data.model_dump());return {'ok':True}
@app.post('/api/applications/{aid}/documents')
async def upload(aid:int,file:UploadFile=File(...),u=Depends(analyst),db=Depends(db_session)):
    get(db,Application,aid); name=Path(file.filename or '').name; ext=Path(name).suffix.lower()
    if ext not in ('.txt','.pdf','.png','.jpg','.jpeg'): raise HTTPException(422,'Supported: PDF, TXT, PNG, JPG')
    content=await file.read(10*1024*1024+1)
    if len(content)>10*1024*1024: raise HTTPException(413,'Maximum 10 MB')
    if ext=='.pdf' and not content.startswith(b'%PDF'): raise HTTPException(422,'Invalid PDF signature')
    folder=ROOT/'data/uploads';folder.mkdir(exist_ok=True);path=folder/(secrets.token_hex(16)+ext);path.write_bytes(content)
    try: text,fields,method,notices=extract(path)
    except Exception as e: path.unlink(missing_ok=True);raise HTTPException(422,'Document processing failed: '+str(e))
    d=Document(application_id=aid,filename=name,storage_name=path.name,text=text,method=method);db.add(d);db.flush()
    for f in fields: db.add(Field(document_id=d.id,**f))
    audit(db,u.username,'document.uploaded',str(aid),{'filename':name,'fields':len(fields),'method':method})
    return dict(id=d.id,fields=fields,notices=notices,method=method)
@app.patch('/api/fields/{fid}')
def correct_field(fid:int,data:FieldInput,u=Depends(analyst),db=Depends(db_session)):
    f=get(db,Field,fid)
    if data.status in ('accepted','corrected') and f.key not in ('employer','address'):
        try:
            value=float(data.value)
            if f.key in Financial.model_fields: Financial(**{f.key:value})
            elif not __import__('math').isfinite(value) or value<0:raise ValueError()
        except Exception:raise HTTPException(422,'Invalid value for '+f.key)
    before=f.value;f.value=data.value;f.status=data.status
    audit(db,u.username,'field.reviewed',str(fid),{'before':before,**data.model_dump()});return row(f)
@app.post('/api/applications/{aid}/apply-fields')
def apply_fields(aid:int,u=Depends(analyst),db=Depends(db_session)):
    a=get(db,Application,aid);c=get(db,Customer,a.customer_id);p={**Financial().model_dump(),**profile(db,c.id)}; applied=[]
    fields=db.scalars(select(Field).join(Document,Field.document_id==Document.id).where(Document.application_id==aid,Field.status.in_(['accepted','corrected'])))
    for f in fields:
        if f.key in p:
            try:p[f.key]=f.value if f.key=='employer' else float(f.value)
            except ValueError:raise HTTPException(422,f'Invalid numeric value for {f.key}')
            applied.append(f.key)
    try: p=Financial(**p).model_dump()
    except Exception: raise HTTPException(422,'Extracted financial values outside accepted ranges')
    old=profile(db,c.id)
    if old.get('income',0)>0 and p['income']>=old['income']*2:db.add(Flag(customer_id=c.id,application_id=aid,category='income',detail=f"Document income {p['income']/old['income']:.2f}x recorded income"))
    db.add(Profile(customer_id=c.id,values=p));audit(db,u.username,'fields.applied',str(aid),{'fields':applied});return {'applied':applied}
@app.post('/api/applications/{aid}/review')
def review(aid:int,data:ReviewInput,u=Depends(reviewer),db=Depends(db_session)):
    a=get(db,Application,aid);ar=latest(db,Assessment,Assessment.application_id,aid)
    if not ar: raise HTTPException(409,'Run assessment before review')
    if a.status in ('approved','declined'): raise HTTPException(409,'Final decision already recorded')
    if data.decision in ('approved','declined') and data.decision!=ar.result['recommendation'] and not data.override: raise HTTPException(422,'Decision differs from model; explicitly mark override')
    if data.override and u.role!='admin': raise HTTPException(403,'Administrator required for credit override')
    r=Review(application_id=aid,assessment_id=ar.id,reviewer=u.username,original=ar.result['recommendation'],decision=data.decision,reason=data.reason,override=int(data.override));db.add(r);a.status=data.decision;a.assigned_to=data.assigned_to
    audit(db,u.username,'credit.override' if data.override else 'review.decision',str(aid),data.model_dump());return {'status':a.status}
@app.get('/api/flags')
def flags(u=Depends(user),db=Depends(db_session)):return [dict(**row(f),customer=get(db,Customer,f.customer_id).name) for f in db.scalars(select(Flag).order_by(Flag.id.desc()))]
@app.patch('/api/flags/{fid}')
def resolve(fid:int,data:Resolution,u=Depends(reviewer),db=Depends(db_session)):
    f=get(db,Flag,fid);f.status=data.status;f.resolution=data.reason;audit(db,u.username,'investigation.updated',str(fid),data.model_dump());return row(f)
@app.post('/api/applications/{aid}/scenario')
def scenario(aid:int,data:Scenario,u=Depends(user),db=Depends(db_session)):
    a=get(db,Application,aid);base=calculate(db,a);stressed=calculate(db,a,data)
    simulation=monte_carlo([stressed],data.iterations,data.correlation)
    return dict(base=base,stressed=stressed,simulation=simulation)
@app.post('/api/applications/{aid}/structure')
def structure(aid:int,u=Depends(analyst),db=Depends(db_session)):
    a=get(db,Application,aid);c=get(db,Customer,a.customer_id);p=profile(db,c.id);base=calculate(db,a)
    max_payment=max(0,p['income']*.5-p['obligations']) if c.kind=='personal' else max(0,(p['cash_flow']/1.2-p['annual_debt_service'])/12)
    alternatives=[]
    for months in sorted(set([a.months,36,60,84])):
        amount=min(a.amount,max_payment/emi(1,a.rate,months))
        if a.secured: amount=min(amount,sum(x['value']*(1-x['haircut']) for x in assets(db,aid))/.8)
        result=assessment(c.kind,p,max(amount,1),a.rate,months,a.secured,assets(db,aid),predict)
        margin=amount*(a.rate-6)/100-result['expected_loss']/max(months/12,1)
        alternatives.append(dict(amount=amount,months=months,rate=a.rate,emi=emi(amount,a.rate,months),expected_loss=result['expected_loss'],annual_margin=margin,raroc=margin/(amount*.12) if amount else 0,feasible=amount>0))
    viable=[x for x in alternatives if x['feasible']]
    best=max(viable,key=lambda x:(x['amount'],x['raroc'])) if viable else None
    result=dict(alternatives=alternatives,optimal=best,assumptions='Maximize lendable principal, then RAROC; personal DTI <=50%, business DSCR >=1.2, secured haircut value >=80% principal. Funding 6%, economic capital 12%, annualized expected loss; educational assumptions.')
    db.add(Structure(application_id=aid,result=result));audit(db,u.username,'structure.calculated',str(aid),result);return result
def portfolio_data(db,kind='',sector=''):
    items=[]
    for a in db.scalars(select(Application)):
        c=get(db,Customer,a.customer_id)
        if (kind and c.kind!=kind) or (sector and c.sector!=sector) or a.status=='declined':continue
        ar=latest(db,Assessment,Assessment.application_id,a.id)
        if ar:items.append(dict(application_id=a.id,name=c.name,kind=c.kind,sector=c.sector,status=a.status,**ar.result))
    return items
@app.get('/api/portfolio')
def portfolio(kind:str='',sector:str='',u=Depends(user),db=Depends(db_session)):
    items=portfolio_data(db,kind,sector);exposure=sum(x['ead'] for x in items)
    def group(key):
        groups={}
        for x in items:
            label=x[key];g=groups.setdefault(label,{'name':label,'exposure':0,'expected_loss':0,'count':0});g['exposure']+=x['ead'];g['expected_loss']+=x['expected_loss'];g['count']+=1
        return list(groups.values())
    approvals=db.scalar(select(func.count()).select_from(Application).where(Application.status=='approved'))
    declines=db.scalar(select(func.count()).select_from(Application).where(Application.status=='declined'))
    loans=list(db.scalars(select(Loan)))
    trends={}
    for a in db.scalars(select(Application)):
        month=a.created[:7];t=trends.setdefault(month,dict(month=month,applications=0,approved=0,declined=0));t['applications']+=1;t['approved']+=int(a.status=='approved');t['declined']+=int(a.status=='declined')
    return dict(customers=db.scalar(select(func.count()).select_from(Customer)),applications=db.scalar(select(func.count()).select_from(Application)),pending=db.scalar(select(func.count()).select_from(Application).where(Application.status.in_(['pending_review','escalated','information_requested']))),flags=db.scalar(select(func.count()).select_from(Flag).where(Flag.status.in_(['open','investigating']))),exposure=exposure,expected_loss=sum(x['expected_loss'] for x in items),high_risk=sum(x['risk_band']=='High' for x in items),approved=approvals,declined=declines,by_sector=group('sector'),by_risk=group('risk_band'),by_product=group('kind'),items=items,trends=sorted(trends.values(),key=lambda x:x['month']),disbursed_count=len(loans),outstanding=sum(x.outstanding for x in loans),scope='Assessed application pipeline, excluding declines; requested principal is exposure proxy. Disbursed balance is reported separately. Trends group current status by application creation month, not decision month.')
@app.post('/api/portfolio/scenario')
def portfolio_stress(data:Scenario,u=Depends(user),db=Depends(db_session)):
    rows=[calculate(db,a,data) for a in db.scalars(select(Application).where(Application.status!='declined')) if latest(db,Assessment,Assessment.application_id,a.id)]
    return monte_carlo(rows,data.iterations,data.correlation)
@app.get('/api/network')
def network(u=Depends(user),db=Depends(db_session)):
    customers=list(db.scalars(select(Customer)));edges=[]
    for i,a in enumerate(customers):
        for b in customers[i+1:]:
            for key in ['phone','address']:
                if getattr(a,key) and getattr(a,key).casefold()==getattr(b,key).casefold():edges.append(dict(source=a.id,target=b.id,label='shared '+key))
    edges += [dict(source=x.customer_id,target=x.related_id,label=x.relation) for x in db.scalars(select(Relationship))]
    return dict(nodes=[dict(id=c.id,name=c.name,kind=c.kind) for c in customers],edges=edges,notice='Shared attributes indicate review candidates, not confirmed fraud.')
@app.get('/api/models')
def models(u=Depends(user),db=Depends(db_session)):
    try: active=metadata()
    except RuntimeError:active=None
    return dict(active=active,versions=[dict(**row(x),notes=[row(n) for n in db.scalars(select(ModelNote).where(ModelNote.model_version==x.id))]) for x in db.scalars(select(ModelVersion).order_by(ModelVersion.created.desc()))])
@app.post('/api/models/train')
def train_models(u=Depends(admin),db=Depends(db_session)):
    result=train();db.add(ModelVersion(id=result['version'],metrics=result));audit(db,u.username,'model.trained',result['version'],{'selected':result['selected']});return result
@app.get('/api/audit')
def audit_events(q:str='',u=Depends(user),db=Depends(db_session)):
    events=list(db.scalars(select(Audit).order_by(Audit.id)))
    return dict(integrity=verify(events),items=[row(x) for x in reversed(events) if q.casefold() in json.dumps(row(x)).casefold()])
@app.get('/api/export/{kind}')
def export(kind:str,u=Depends(user),db=Depends(db_session)):
    if kind=='audit':
        content=json.dumps([row(x) for x in db.scalars(select(Audit).order_by(Audit.id))],indent=2);media='application/json';ext='json'
    elif kind=='portfolio':
        buf=io.StringIO();writer=csv.writer(buf);writer.writerow(['application_id','customer','sector','status','ead','pd','lgd','expected_loss'])
        for x in portfolio_data(db):writer.writerow([x['application_id'],x['name'],x['sector'],x['status'],x['ead'],x['pd'],x['lgd'],x['expected_loss']])
        content=buf.getvalue();media='text/csv';ext='csv'
    else: raise HTTPException(404,'Export not found')
    return Response(content,media_type=media,headers={'Content-Disposition':f'attachment; filename="orion-{kind}.{ext}"'})
@app.get('/api/applications/{aid}/memo')
def memo(aid:int,u=Depends(user),db=Depends(db_session)):
    a=get(db,Application,aid);c=get(db,Customer,a.customer_id);ar=latest(db,Assessment,Assessment.application_id,aid)
    if not ar:raise HTTPException(409,'Assess before generating memo')
    result=ar.result
    content=f'# ORION Credit Memo — APP-{aid}\n\nFictional academic demonstration. Deterministic narrative.\n\nCustomer: {c.name}\nRequested: INR {a.amount:,.2f}; {a.months} months at {a.rate}%\n\nModel recommendation: {result["recommendation"]}\nHuman workflow status: {a.status}\nPD: {result["pd"]:.2%}; LGD: {result["lgd"]:.2%}; Expected loss: INR {result["expected_loss"]:,.2f}\n\nReasons:\n'+ '\n'.join('- '+r for r in result['reasons'])+'\n\n'+result['assumptions']+'\n\nModel version: '+ar.model_version
    return Response(content,media_type='text/markdown',headers={'Content-Disposition':f'attachment; filename="ORION-APP-{aid}-memo.md"'})

@app.post('/api/documents/{did}/credit-report')
def import_credit_report(did:int,u=Depends(analyst),db=Depends(db_session)):
    d=get(db,Document,did)
    if db.scalar(select(CreditReport).where(CreditReport.document_id==did)):raise HTTPException(409,'Report already imported')
    try:accounts=credit_accounts(d.text)
    except ValueError as e:raise HTTPException(422,str(e))
    if not accounts:raise HTTPException(422,'No supported Account: rows; see sample_data/personal_credit_report.txt')
    reviewed=list(db.scalars(select(Field).where(Field.document_id==did,Field.status.in_(['accepted','corrected']))))
    score=next((int(float(f.value)) for f in reviewed if f.key=='credit_score'),None)
    inquiries=next((int(float(f.value)) for f in reviewed if f.key=='inquiries'),0)
    r=CreditReport(application_id=d.application_id,document_id=did,reported_score=score,inquiries=inquiries,reviewed_by=u.username);db.add(r);db.flush()
    for x in accounts:db.add(CreditAccount(report_id=r.id,**x))
    audit(db,u.username,'credit_report.imported',str(d.application_id),{'document_id':did,'accounts':len(accounts)});return dict(id=r.id,accounts=accounts)
@app.post('/api/applications/{aid}/disburse')
def disburse(aid:int,data:Disbursement,u=Depends(reviewer),db=Depends(db_session)):
    a=get(db,Application,aid)
    if a.status!='approved':raise HTTPException(409,'Approval required before disbursement')
    if db.scalar(select(Loan).where(Loan.application_id==aid)):raise HTTPException(409,'Facility already disbursed')
    loan=Loan(application_id=aid,principal=a.amount,outstanding=a.amount,disbursed_date=data.date);db.add(loan);audit(db,u.username,'loan.disbursed',str(aid),data.model_dump());return {'ok':True}
@app.post('/api/applications/{aid}/repayments')
def repayment(aid:int,data:RepaymentInput,u=Depends(reviewer),db=Depends(db_session)):
    a=get(db,Application,aid);loan=db.scalar(select(Loan).where(Loan.application_id==aid))
    if not loan:raise HTTPException(409,'Disburse facility before recording repayments')
    if data.principal_paid>min(data.amount,loan.outstanding):raise HTTPException(422,'Principal component exceeds payment or outstanding balance')
    if data.date<loan.disbursed_date:raise HTTPException(422,'Payment predates disbursement')
    db.add(Repayment(application_id=aid,date=data.date,amount=data.amount,days_past_due=data.days_past_due));loan.outstanding-=data.principal_paid
    audit(db,u.username,'repayment.recorded',str(aid),data.model_dump());return {'outstanding':loan.outstanding}
@app.get('/api/users')
def users(u=Depends(admin),db=Depends(db_session)):return [dict(id=x.id,username=x.username,role=x.role) for x in db.scalars(select(User))]
@app.post('/api/users')
def create_user(data:UserInput,u=Depends(admin),db=Depends(db_session)):
    if db.scalar(select(User).where(User.username==data.username)):raise HTTPException(409,'Username exists')
    db.add(User(username=data.username,password=password_hash(data.password),role=data.role));audit(db,u.username,'user.created',data.username,{'role':data.role});return {'username':data.username,'role':data.role}
@app.post('/api/models/{version}/validation')
def validate_model(version:str,data:ValidationInput,u=Depends(admin),db=Depends(db_session)):
    get(db,ModelVersion,version);db.add(ModelNote(model_version=version,author=u.username,**data.model_dump()));audit(db,u.username,'model.validation',version,data.model_dump());return {'ok':True}
@app.post('/api/models/{version}/activate')
def activate_model(version:str,u=Depends(admin),db=Depends(db_session)):
    get(db,ModelVersion,version)
    from src.model import ROOT as MODEL_ROOT,_cache
    if not (MODEL_ROOT/version/'metrics.json').exists():raise HTTPException(409,'Model artifact unavailable')
    note=latest(db,ModelNote,ModelNote.model_version,version)
    if note and note.status=='retired':raise HTTPException(409,'Retired model cannot be activated')
    temp=MODEL_ROOT/'active.tmp';temp.write_text(json.dumps({'version':version}));temp.replace(MODEL_ROOT/'active.json');_cache.clear();audit(db,u.username,'model.activated',version);return {'active':version}

dist=ROOT/'frontend/dist'
if dist.exists():
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from fastapi.responses import FileResponse
    class SPAFiles(StaticFiles):
        async def get_response(self,path,scope):
            try: return await super().get_response(path,scope)
            except StarletteHTTPException as e:
                if e.status_code==404 and not path.startswith('api/') and '.' not in path: return FileResponse(dist/'index.html')
                raise
    app.mount('/',SPAFiles(directory=dist,html=True),name='frontend')
