"""Independent contract checks over serialized rows and raw source timestamps."""
import json
from .models import timestamp
from .compiler import HEADER,FIELDS,OPERATIONS,sort_key
from .loader import read_csv


def validate_audit(audit, sources):
    steps = audit.steps
    if not isinstance(steps,list) or any(not isinstance(s,dict) for s in steps):
        raise ValueError('steps_json must contain an array of step objects')
    if audit.status not in ('COMPLETE','INCOMPLETE','NOT_APPLICABLE'):
        raise ValueError('Invalid deletion status')
    if audit.status=='NOT_APPLICABLE':
        if steps: raise ValueError('Non-deletion request has steps')
        return
    if not steps: raise ValueError('Authorized case has no source-derived verification')
    seen=set()
    for n,step in enumerate(steps,1):
        if set(step)!=FIELDS or type(step['step_no']) is not int or step['step_no']!=n:
            raise ValueError('Invalid exact seven-field step schema or numbering')
        if any(not isinstance(step[k],str) for k in FIELDS-{'step_no'}):
            raise ValueError('Non-string step field')
        if step['phase'] not in OPERATIONS or step['operation'] not in OPERATIONS[step['phase']]:
            raise ValueError('Invalid phase/operation')
        if step['state']!=OPERATIONS[step['phase']][step['operation']]:
            raise ValueError('Invalid operation/state pair')
        if not step['system_id'] or not step['resource_id']: raise ValueError('Empty resource scope')
        key=(step['phase'],step['operation'],step['system_id'],step['resource_id'])
        if key in seen: raise ValueError('Duplicate step')
        seen.add(key)
        needs_source = step['phase']=='FINDING' or audit.status=='COMPLETE'
        if needs_source:
            source=step['evidence_id']
            if source not in sources or sources[source]>timestamp(audit.case['audit_at']):
                raise ValueError('Unknown or future evidence citation')
        elif step['evidence_id']: raise ValueError('Future operation must not cite evidence')
        if audit.status=='COMPLETE' and step['phase']!='VERIFICATION':
            raise ValueError('Complete case has nonverification step')
    if audit.status=='INCOMPLETE' and {s['phase'] for s in steps} != set(OPERATIONS):
        raise ValueError('Incomplete case must include all three phases')
    if steps != sorted(steps,key=sort_key): raise ValueError('Noncanonical step sequence')


def validate_file(path,cases,sources):
    from .models import Audit
    rows=read_csv(path,','.join(HEADER))
    if [r['case_id'] for r in rows]!=sorted(c['case_id'] for c in cases):
        raise ValueError('Missing, duplicate, extra or unsorted cases')
    by_id={c['case_id']:c for c in cases}
    for row in rows:
        steps=json.loads(row['steps_json'])
        if not isinstance(steps,list): raise ValueError('steps_json must be an array')
        validate_audit(Audit(by_id[row['case_id']],'',[],row['deletion_status'],steps),sources)
    return len(rows)
