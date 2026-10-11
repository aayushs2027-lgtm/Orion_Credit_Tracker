"""Bureau tradelines, disbursed facilities and validation notes."""
from alembic import op
from backend.database import CreditReport,CreditAccount,Loan,ModelNote
revision='002'
down_revision='001'
branch_labels=None
depends_on=None
def upgrade():
    for cls in (CreditReport,CreditAccount,Loan,ModelNote):cls.__table__.create(op.get_bind(),checkfirst=True)
def downgrade():
    for cls in (ModelNote,Loan,CreditAccount,CreditReport):cls.__table__.drop(op.get_bind(),checkfirst=True)
