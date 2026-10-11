"""Reproducible educational dataset. Never use as evidence of bank performance."""
import numpy as np
import pandas as pd
FEATURES=['credit_score','repayment_burden','delinquencies','utilization','stability_years','business']
def dataset(n=1800,seed=42):
    rng=np.random.default_rng(seed)
    x=pd.DataFrame(dict(credit_score=rng.integers(350,851,n),repayment_burden=rng.uniform(.05,1.8,n),delinquencies=rng.poisson(.6,n),utilization=rng.uniform(0,1,n),stability_years=rng.uniform(0,20,n),business=rng.integers(0,2,n)))
    logits=-2.8+(650-x.credit_score)/100+1.8*x.repayment_burden+.65*x.delinquencies+1.2*x.utilization-.07*x.stability_years+.15*x.business
    y=rng.binomial(1,1/(1+np.exp(-logits)))
    return x,y
