import json, threading
from datetime import datetime, timezone
from pathlib import Path
import joblib, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, confusion_matrix, brier_score_loss
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier
from .data import dataset, FEATURES
ROOT=Path(__file__).resolve().parents[1]/'artifacts'
ROOT.mkdir(exist_ok=True)
LOCK=threading.Lock()
_cache={}

def train():
    with LOCK:
        x,y=dataset()
        xt,xs,yt,ys=train_test_split(x,y,test_size=.2,stratify=y,random_state=42)
        cv=StratifiedKFold(5,shuffle=True,random_state=42)
        candidates={
            'Logistic Regression':(Pipeline([('scale',StandardScaler()),('model',LogisticRegression(max_iter=1000,random_state=42))]),{'model__C':[.1,1,10]}),
            'Random Forest':(RandomForestClassifier(n_estimators=100,random_state=42,n_jobs=1),{'max_depth':[4,8],'min_samples_leaf':[5,15]}),
            'XGBoost':(XGBClassifier(n_estimators=100,random_state=42,n_jobs=1,eval_metric='logloss'),{'max_depth':[2,4],'learning_rate':[.05,.1]})}
        version=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
        folder=ROOT/version; folder.mkdir()
        metrics=[]
        for name,(model,params) in candidates.items():
            search=GridSearchCV(model,params,cv=cv,scoring='roc_auc',n_jobs=1).fit(xt,yt)
            best=search.best_estimator_; prob=best.predict_proba(xs)[:,1]; label=prob>=.3
            observed,predicted=calibration_curve(ys,prob,n_bins=8)
            row=dict(name=name,cv_auc=float(search.best_score_),cv_std=float(search.cv_results_['std_test_score'][search.best_index_]),roc_auc=float(roc_auc_score(ys,prob)),pr_auc=float(average_precision_score(ys,prob)),precision=float(precision_score(ys,label,zero_division=0)),recall=float(recall_score(ys,label)),f1=float(f1_score(ys,label)),brier=float(brier_score_loss(ys,prob)),confusion=confusion_matrix(ys,label).tolist(),parameters=search.best_params_,calibration=[dict(predicted=float(p),observed=float(o)) for p,o in zip(predicted,observed)],errors=dict(false_positive=int(((label==1)&(ys==0)).sum()),false_negative=int(((label==0)&(ys==1)).sum())))
            metrics.append(row); joblib.dump(best,folder/(name+'.joblib'))
        selected=max(metrics,key=lambda m:m['cv_auc'])['name']
        joblib.dump(xt.iloc[:100],folder/'background.joblib')
        joblib.dump(IsolationForest(random_state=42,contamination=.08).fit(xt),folder/'anomaly.joblib')
        result=dict(version=version,selected=selected,candidates=metrics,features=FEATURES,training_rows=len(xt),test_rows=len(xs),seed=42,threshold=.3,source='Synthetic educational dataset; no real bank outcomes. Selection by training CV only; test set untouched by tuning.',limitations=['Random split is not out-of-time validation','Synthetic relationships do not establish external validity','Not approved for real lending or demographic fairness claims'])
        (folder/'metrics.json').write_text(json.dumps(result,indent=2))
        (ROOT/'active.json').write_text(json.dumps({'version':version}))
        _cache.clear()
        return result

def metadata():
    if not (ROOT/'active.json').exists(): raise RuntimeError('Train models before assessing applications')
    version=json.loads((ROOT/'active.json').read_text())['version']
    return json.loads((ROOT/version/'metrics.json').read_text())

def predict(values,algorithm=None):
    m=metadata(); version=m['version']; folder=ROOT/version
    name=algorithm or m['selected']
    if name not in ('Logistic Regression','Random Forest','XGBoost'):raise ValueError('Unknown algorithm')
    key=(version,name)
    if key not in _cache:
        _cache[key]=(joblib.load(folder/(name+'.joblib')),joblib.load(folder/'background.joblib'),joblib.load(folder/'anomaly.joblib'))
    model,bg,anomaly=_cache[key]
    x=pd.DataFrame([values],columns=FEATURES)
    import shap
    if isinstance(model,Pipeline):
        scaler=model.named_steps['scale']; transformed=scaler.transform(x)
        explainer=shap.LinearExplainer(model.named_steps['model'],scaler.transform(bg))
        explanation=explainer(transformed); unit='log odds'
    else:
        explainer=shap.TreeExplainer(model); explanation=explainer(x); unit='probability' if name=='Random Forest' else 'log odds'
    sv=np.asarray(explanation.values)
    if sv.ndim==3: contributions=sv[0,:,1]; base=float(np.asarray(explanation.base_values)[0,1])
    else: contributions=sv[0]; base=float(np.asarray(explanation.base_values).reshape(-1)[0])
    return dict(pd=float(model.predict_proba(x)[0,1]),model_version=version,model=name,features=dict(zip(FEATURES,values)),shap=[dict(feature=f,value=float(v),input=float(i)) for f,v,i in zip(FEATURES,contributions,values)],shap_base=base,shap_units=unit,anomaly_score=float(-anomaly.score_samples(x)[0]),anomaly_flag=bool(anomaly.predict(x)[0]==-1))
