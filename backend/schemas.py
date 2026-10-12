from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class Login(Strict):
    username:str=Field(min_length=1,max_length=100)
    password:str=Field(min_length=1,max_length=200)
class Financial(Strict):
    previous_year_revenue:float|None=Field(default=None,ge=0,le=1e14)
    revenue_year:int|None=Field(default=None,ge=1900,le=2100)
    previous_revenue_year:int|None=Field(default=None,ge=1900,le=2100)
    @model_validator(mode='after')
    def revenue_periods(self):
        if self.previous_year_revenue is not None:
            if self.revenue_year is None or self.previous_revenue_year is None or self.revenue_year-self.previous_revenue_year!=1:
                raise ValueError('Revenue comparison requires consecutive reporting years')
        return self
    employer:str=Field(default='',max_length=200)
    management_quality:int=Field(default=50,ge=0,le=100)
    income:float=Field(default=0,ge=0,le=1e12)
    obligations:float=Field(default=0,ge=0,le=1e12)
    revenue:float=Field(default=0,ge=0,le=1e14)
    ebitda:float=Field(default=0,ge=-1e14,le=1e14)
    cash_flow:float=Field(default=0,ge=-1e14,le=1e14)
    annual_debt_service:float=Field(default=0,ge=0,le=1e14)
    interest_expense:float=Field(default=0,ge=0,le=1e14)
    current_assets:float=Field(default=0,ge=0,le=1e14)
    current_liabilities:float=Field(default=0,ge=0,le=1e14)
    total_debt:float=Field(default=0,ge=0,le=1e14)
    equity:float=Field(default=0,ge=0,le=1e14)
    net_profit:float=Field(default=0,ge=-1e14,le=1e14)
    credit_score:int=Field(default=650,ge=300,le=900)
    delinquencies:int=Field(default=0,ge=0,le=100)
    utilization:float=Field(default=.3,ge=0,le=1)
    stability_years:float=Field(default=3,ge=0,le=100)
class CustomerInput(Strict):
    kind:Literal['personal','business']
    name:str=Field(min_length=2,max_length=150)
    identity:str=Field(min_length=3,max_length=80)
    email:str=Field(default='',max_length=150)
    address:str=Field(min_length=3,max_length=500)
    phone:str=Field(default='',max_length=30)
    sector:str=Field(default='Retail',max_length=100)
    financial:Financial
class ApplicationInput(Strict):
    customer_id:int
    amount:float=Field(gt=0,le=1e12)
    rate:float=Field(ge=0,le=60)
    months:int=Field(ge=1,le=480)
    secured:bool=False
class AssetInput(Strict):
    category:str=Field(min_length=2,max_length=100)
    value:float=Field(gt=0,le=1e14)
    haircut:float=Field(ge=0,le=1)
    valuation_date:str
    @field_validator('valuation_date')
    @classmethod
    def date_valid(cls,v):
        from datetime import date
        date.fromisoformat(v)
        return v
class ReviewInput(Strict):
    decision:Literal['approved','declined','escalated','information_requested']
    reason:str=Field(min_length=10,max_length=2000)
    override:bool=False
    assigned_to:str=Field(default='Unassigned',max_length=100)
class FieldInput(Strict):
    value:str=Field(max_length=1000)
    status:Literal['accepted','corrected','flagged']
class Resolution(Strict):
    status:Literal['investigating','resolved','dismissed','escalated','verified','manager_approved']
    reason:str=Field(min_length=10,max_length=2000)
    assigned_team:str=Field(default='',max_length=100)
    @field_validator('reason',mode='before')
    @classmethod
    def meaningful_reason(cls,v):
        return v.strip() if isinstance(v,str) else v
class Scenario(Strict):
    income_shock:float=Field(default=0,ge=-95,le=100)
    revenue_shock:float=Field(default=0,ge=-95,le=100)
    expense_shock:float=Field(default=0,ge=0,le=200)
    rate_change:float=Field(default=0,ge=-20,le=20)
    collateral_shock:float=Field(default=0,ge=-95,le=100)
    pd_multiplier:float=Field(default=1,ge=.1,le=5)
    iterations:int=Field(default=2000,ge=100,le=20000)
    correlation:float=Field(default=.25,ge=0,le=.95)
class RelationshipInput(Strict):
    related_id:int
    relation:str=Field(min_length=2,max_length=100)
class UserInput(Strict):
    username:str=Field(min_length=3,max_length=100,pattern=r'^[A-Za-z0-9_.-]+$')
    password:str=Field(min_length=12,max_length=200)
    role:Literal['viewer','analyst','reviewer','admin']
class ValidationInput(Strict):
    status:Literal['candidate','validated','retired']
    note:str=Field(min_length=10,max_length=4000)
class Disbursement(Strict):
    date:str
    @field_validator('date')
    @classmethod
    def validate_date(cls,v):
        from datetime import date
        date.fromisoformat(v)
        if date.fromisoformat(v)>date.today():raise ValueError('Disbursement date cannot be future')
        return v
class RepaymentInput(Disbursement):
    amount:float=Field(gt=0,le=1e12)
    principal_paid:float=Field(ge=0,le=1e12)
    days_past_due:int=Field(ge=0,le=1000)
