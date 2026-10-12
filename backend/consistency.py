"""Evidence integrity checks; thresholds are educational review policies, not fraud verdicts."""
import re
from sqlalchemy import select
from .database import Flag

def normalized_address(value):
    return re.sub(r'[^\w]+', ' ', value.casefold()).strip()

def record_flag(db, customer_id, application_id, category, detail):
    # Reapplying the same reviewed evidence must not create duplicate work items.
    existing=db.scalar(select(Flag).where(Flag.customer_id==customer_id,Flag.category==category,Flag.detail==detail))
    if not existing:
        db.add(Flag(customer_id=customer_id,application_id=application_id,category=category,detail=detail))

def revenue_check(db, customer, values):
    previous=values.get('previous_year_revenue')
    if customer.kind!='business' or previous is None:
        return
    current=values['revenue']
    growth=(current-previous)/previous*100 if previous>0 else None
    if (growth is not None and growth>=200) or (previous==0 and current>0):
        change=f'{growth:.1f}% growth' if growth is not None else 'Growth percentage undefined because prior revenue is zero'
        detail=f"Reported annual revenue: {values['previous_revenue_year']} INR {previous:,.2f} → {values['revenue_year']} INR {current:,.2f}. {change}. Verify financial statements and revenue recognition; educational review threshold: 200%."
        record_flag(db,customer.id,None,'revenue_growth',detail)
