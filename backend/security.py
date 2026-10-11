import hashlib, hmac, secrets, json
from sqlalchemy import select
from .database import Audit, now

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    return salt + ':' + hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
def password_matches(password, stored):
    return hmac.compare_digest(password_hash(password, stored.split(':')[0]), stored)
def digest(actor, action, entity, payload, created, previous):
    return hashlib.sha256(json.dumps([actor, action, entity, payload, created, previous], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def audit(db, actor, action, entity, payload=None):
    db.flush()
    last = db.scalar(select(Audit).order_by(Audit.id.desc()).limit(1))
    created, previous, payload = now(), last.hash if last else '0'*64, payload or {}
    db.add(Audit(actor=actor, action=action, entity=entity, payload=payload, created=created, previous_hash=previous, hash=digest(actor, action, entity, payload, created, previous)))
    db.flush()
def verify(events):
    previous = '0'*64
    for e in events:
        if e.previous_hash != previous or e.hash != digest(e.actor,e.action,e.entity,e.payload,e.created,e.previous_hash): return False
        previous = e.hash
    return True
