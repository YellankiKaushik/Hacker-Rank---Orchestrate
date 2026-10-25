"""Small reviewer invariants over original values; no primary semantic imports.

These are independently reasoned vetoes, not another complete inference engine.
Schema/SQLite extraction is shared; authorization and identifier/control witnesses
here do not call intent.deletion_intent, adapters.state_of or Policy.
"""
import json
import re
import unicodedata
from datetime import datetime


def authorization_veto(text):
    t=unicodedata.normalize('NFKC',text).casefold().replace('’',"'")
    clauses=re.split(r'[;.!\n]',t)
    if re.search(r'\bnot\s+(?:asking|requesting|authori[sz]ing)(?:\s+you)?\s+to\s+(?:delete|erase|remove|close)\b.{0,30}\b(?:account|profile|data|records)\b',t):
        return 'Original request withholds the proposed erasure action'
    affirmative=False
    for clause in clauses:
        if re.search(r'\b(?:not|never)\s+(?:request\w*|authori[sz]\w*|seek\w*|asking(?:\s+for)?)\s+(?:(?:any|account|data|the)\s+)*(?:deletion|erasure|removal|closure)',clause):
            return 'Original request explicitly withholds deletion authorization'
        if re.search(r"(?:do not|don't|never)\s+(?:delete|erase|remove|close).{0,25}(?:account|profile|personal|data|anything)",clause):
            return 'Original request forbids deletion of the subject records'
        information=bool(re.search(r'\b(?:explain|describe|tell me|what|how|whether|information about)\b',clause))
        if not information and re.search(r'\b(?:delete|erase|remove|close|purge|destroy|dispose)\b.{0,100}\b(?:account|profile|personal|data|records|search|identifiers)\b|\b(?:want|wish|request\w*|ask\w*|authori[sz]\w*)\b.{0,100}\b(?:deletion|erasure|removed|deleted|erased)\b',clause):
            affirmative=True
    if affirmative:return ''
    if re.search(r'\b(?:explain|describe|tell me about|what|how|whether|information about)\b.{0,100}\b(?:delet\w*|eras\w*|removal|closure)\b',t):
        return 'Original request asks for information without an affirmative erasure directive'
    if re.search(r'\b(?:freeze|suspend|pause|deactivate)\b.{0,50}\b(?:temporarily|temporary|for now)\b',t):
        return 'Temporary suspension does not authorize erasure'
    # Other languages/indirect requests still require existing provenance and
    # domain checks. An empty veto is not independently positive authorization.
    return ''


def identifier_paths(record,category):
    """Return field paths, never sensitive field values or unrelated row content."""
    direct={'email','phone','email_hash','full_name','name','display_name','requester_name',
            'requester_email','requester_phone','owner_email','owner_phone','customer_email'}
    stable={'user_id','customer_reference','subject_reference'} if category in ('ANALYTICS_PROFILE','PRODUCT_TELEMETRY') else set()
    empty={'','null','none','[redacted]','redacted','no direct identifier'}
    found=[]
    def walk(value,path=''):
        if isinstance(value,list):
            for n,item in enumerate(value):walk(item,f'{path}/{n}')
        elif isinstance(value,dict):
            for k,v in value.items():
                p=path+'/'+k
                selector=k=='subject_reference' and 'record_type' in value and 'result' in value
                if k in direct|stable and not selector and v is not None and str(v).strip().casefold() not in empty:
                    found.append(p)
                if isinstance(v,(dict,list)):walk(v,p)
    walk(record)
    return found


def original_records(raw,suffix,scope,locator,resource,observed):
    """Locate only the target original row; never inspect neighboring identities."""
    if suffix=='.sql':
        return [json.loads(r['record_json']) if 'record_json' in r else r
                for r in raw.get(scope,[]) if r.get('resource_id')==resource]
    if suffix=='.json':
        found=[]
        def walk(v,time=None):
            if isinstance(v,dict):
                time=next((v[k] for k in ('observed_at','recorded_at','captured_at','exported_at') if k in v),time)
                if v.get('resource_id')==resource and (time is None or datetime.fromisoformat(time.replace('Z','+00:00'))==observed):found.append(v)
                for x in v.values():walk(x,time)
            elif isinstance(v,list):
                for x in v:walk(x,time)
        walk(json.loads(raw))
        return found
    if suffix=='.log' and locator.startswith('line:'):
        line=raw.splitlines()[int(locator.split(':')[1])-1]
        payload=re.sub(r'^\S+\s+','',line).strip()
        if payload.startswith('{'):return [json.loads(payload)]
        return [{k:q or b for k,q,b in re.findall(r'(\w+)=(?:"([^"]*)"|([^\s"]+))',payload.replace('\\"','"'))}]
    return []


def raw_state_veto(fact,records):
    for row in records:
        if fact.state in ('REDACTED','ANONYMIZED'):
            paths=identifier_paths(row,fact.category)
            if paths:return 'Original fields contradict compliant state: '+','.join(paths)
        if fact.state=='ABSENT':
            if row.get('result') in ('FOUND','PRESENT') or re.fullmatch(r'[1-9]\d*',str(row.get('rows',''))):
                return 'Original positive readback contradicts absence'
        if fact.category in ('DATA_FLOW','BACKUP_ARCHIVE'):
            controls=[]
            for key,inverse in ({'enabled':False,'disabled':True} if fact.category=='DATA_FLOW' else {'restore_allowed':False,'eligible':False,'restore_blocked':True}).items():
                if key not in row:continue
                token=row[key].strip().casefold() if isinstance(row[key],str) else row[key]
                value={True:True,False:False,'true':True,'false':False,'1':True,'0':False}.get(token if isinstance(token,(str,bool,int)) else None)
                if value is None:return 'Original control value is not an explicit boolean'
                controls.append(not value if inverse else value)
            if controls and (len(set(controls))!=1 or (fact.state=='ACTIVE')!=controls[0]):
                return 'Original controls contradict proposed process state'
    return ''


def raw_operation_veto(fact,records,operation,cutoff,catalog_details=''):
    if operation=='DELETE_RECORD':
        if fact.category in ('ACCOUNT_TOMBSTONE','BACKUP_ARCHIVE'):
            return 'Original policy preserves this reference/archive'
        if fact.category=='SUPPORT_ATTACHMENT':
            explicit=('belongs only to' in catalog_details.casefold() and 'no other subject is linked' in catalog_details.casefold())
            for row in records:
                owners=row.get('shared_subjects',[])
                if isinstance(owners,list) and len(set(owners))>1:return 'Original attachment has multiple known subjects'
                explicit=explicit or row.get('sole_owner') is True or str(row.get('sole_owner','')).casefold() in ('true','1')
            if not explicit:return 'Original attachment has no exclusivity witness'
        if fact.category in ('SECURITY_AUDIT_LOG','LEGAL_HOLD_RECORD'):
            for row in records:
                active=row.get('retention_active') if fact.category=='SECURITY_AUDIT_LOG' else row.get('legal_hold_active')
                until=row.get('retention_until') or row.get('retained_until')
                if until and datetime.fromisoformat(until.replace('Z','+00:00'))>=cutoff:
                    return 'Original retained-until date prohibits deletion at cutoff'
                if not until and (active is True or str(active).casefold() in ('true','1')):
                    return 'Original active retention/hold prohibits deletion'
    # A future check after disabling/blocking is a plan, not a claim that the
    # current ACTIVE process already has the requested final state.
    if operation in ('VERIFY_RESTORE_BLOCKED','VERIFY_DATA_FLOW_DISABLED') and records and fact.state in ('BLOCKED','DISABLED'):
        for row in records:
            keys={'enabled','disabled'} if fact.category=='DATA_FLOW' else {'restore_allowed','restore_blocked','eligible','decision'}
            claim=row.get('result') if 'record_type' in row else row.get('_state')
            if not keys.intersection(row) and claim not in ('DISABLED','BLOCKED'):
                return 'Original process readback lacks configuration/permission proof'
    return ''
