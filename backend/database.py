import os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine, event, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.types import JSON, String, Float, Integer

ROOT = Path(__file__).resolve().parents[1]
(ROOT / 'data').mkdir(exist_ok=True)
engine = create_engine(os.getenv('ORION_DATABASE_URL', 'sqlite:///' + str(ROOT / 'data/orion.db')), connect_args={'check_same_thread': False} if os.getenv('ORION_DATABASE_URL', 'sqlite:').startswith('sqlite:') else {})
if engine.dialect.name == 'sqlite':
    @event.listens_for(engine, 'connect')
    def sqlite_fk(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
Session = sessionmaker(engine, expire_on_commit=False)
def now(): return datetime.now(timezone.utc).isoformat()
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str]
    role: Mapped[str]
class Token(Base):
    __tablename__ = 'sessions'
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    expires: Mapped[float]
class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str]
    name: Mapped[str]
    identity: Mapped[str] = mapped_column(String(80), unique=True)
    email: Mapped[str]
    address: Mapped[str]
    phone: Mapped[str]
    sector: Mapped[str]
    created: Mapped[str] = mapped_column(default=now)
class Profile(Base):
    __tablename__ = 'financial_profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    values: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(default=now)
class Application(Base):
    __tablename__ = 'applications'
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    amount: Mapped[float]
    rate: Mapped[float]
    months: Mapped[int]
    secured: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(default='draft')
    assigned_to: Mapped[str] = mapped_column(default='Unassigned')
    created: Mapped[str] = mapped_column(default=now)
class Collateral(Base):
    __tablename__ = 'collateral'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    category: Mapped[str]
    value: Mapped[float]
    haircut: Mapped[float]
    valuation_date: Mapped[str]
class Assessment(Base):
    __tablename__ = 'assessments'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    model_version: Mapped[str]
    result: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(default=now)
class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    filename: Mapped[str]
    storage_name: Mapped[str]
    text: Mapped[str]
    method: Mapped[str]
    created: Mapped[str] = mapped_column(default=now)
class Field(Base):
    __tablename__ = 'extracted_fields'
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'))
    key: Mapped[str]
    value: Mapped[str]
    page: Mapped[int]
    evidence: Mapped[str]
    confidence: Mapped[float]
    status: Mapped[str] = mapped_column(default='pending')
class Flag(Base):
    __tablename__ = 'discrepancies'
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    application_id: Mapped[int | None] = mapped_column(ForeignKey('applications.id'), nullable=True)
    category: Mapped[str]
    detail: Mapped[str]
    status: Mapped[str] = mapped_column(default='open')
    resolution: Mapped[str] = mapped_column(default='')
    created: Mapped[str] = mapped_column(default=now)
class Review(Base):
    __tablename__ = 'reviews'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    assessment_id: Mapped[int] = mapped_column(ForeignKey('assessments.id'))
    reviewer: Mapped[str]
    original: Mapped[str]
    decision: Mapped[str]
    reason: Mapped[str]
    override: Mapped[int]
    created: Mapped[str] = mapped_column(default=now)
class ModelVersion(Base):
    __tablename__ = 'model_versions'
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    metrics: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(default=now)
class Audit(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str]
    action: Mapped[str]
    entity: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(default=now)
    previous_hash: Mapped[str]
    hash: Mapped[str]
class Relationship(Base):
    __tablename__ = 'relationships'
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    related_id: Mapped[int] = mapped_column(ForeignKey('customers.id'))
    relation: Mapped[str]
class Repayment(Base):
    __tablename__ = 'repayments'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    date: Mapped[str]
    amount: Mapped[float]
    days_past_due: Mapped[int]
class Structure(Base):
    __tablename__ = 'loan_structures'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    result: Mapped[dict] = mapped_column(JSON)
    created: Mapped[str] = mapped_column(default=now)
class CreditReport(Base):
    __tablename__ = 'credit_reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'))
    reported_score: Mapped[int | None] = mapped_column(nullable=True)
    inquiries: Mapped[int] = mapped_column(default=0)
    reviewed_by: Mapped[str]
    created: Mapped[str] = mapped_column(default=now)
class CreditAccount(Base):
    __tablename__ = 'credit_accounts'
    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey('credit_reports.id'))
    creditor: Mapped[str]
    account_type: Mapped[str]
    outstanding: Mapped[float]
    credit_limit: Mapped[float]
    monthly_payment: Mapped[float]
    days_past_due: Mapped[int]
    history: Mapped[str]
    source_line: Mapped[str]
class Loan(Base):
    __tablename__ = 'loans'
    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'),unique=True)
    principal: Mapped[float]
    outstanding: Mapped[float]
    disbursed_date: Mapped[str]
class ModelNote(Base):
    __tablename__ = 'model_validation_notes'
    id: Mapped[int] = mapped_column(primary_key=True)
    model_version: Mapped[str] = mapped_column(ForeignKey('model_versions.id'))
    author: Mapped[str]
    status: Mapped[str]
    note: Mapped[str]
    created: Mapped[str] = mapped_column(default=now)
