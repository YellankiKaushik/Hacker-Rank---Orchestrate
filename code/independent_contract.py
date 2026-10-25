"""Independent official CSV/JSON contract checker; no production imports.

Reports every invalid case. A best-effort candidate never waives plan phases.
Reference/time checks do not certify source semantics or missing obligations.
"""
import argparse
import csv
import json
from pathlib import Path
from datetime import datetime

ORDER={
 'FINDING':[('REPORT_REMAINING_RECORD','PRESENT'),('REPORT_EXPOSED_PII','PRESENT'),('REPORT_ACTIVE_DATA_FLOW','ACTIVE'),('REPORT_RESTORE_RISK','ACTIVE')],
 'REMEDIATION':[('DISABLE_DATA_FLOW','DISABLED'),('BLOCK_RESTORE','BLOCKED'),('DELETE_RECORD','ABSENT'),('REDACT_RECORD','REDACTED'),('ANONYMIZE_RECORD','ANONYMIZED')],
 'VERIFICATION':[('VERIFY_RECORD_ABSENT','ABSENT'),('VERIFY_RECORD_PRESENT','PRESENT'),('VERIFY_RECORD_REDACTED','REDACTED'),('VERIFY_RECORD_ANONYMIZED','ANONYMIZED'),('VERIFY_DATA_FLOW_DISABLED','DISABLED'),('VERIFY_RESTORE_BLOCKED','BLOCKED')]}
FIELDS={'step_no','phase','system_id','resource_id','operation','state','evidence_id'}
def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f); return r.fieldnames,list(r)
def time(value):
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('Timezone required')
    return t
def check(path,requests,sources=None):
    header,rows=read(path);_,cases=read(requests);expected={r['case_id']:r for r in cases}
    shape=[];plans=[];citations=[]
    if header!=['case_id','deletion_status','steps_json']:shape.append({'case_id':'*','error':'Wrong header'})
    if [r.get('case_id') for r in rows]!=sorted(expected):shape.append({'case_id':'*','error':'Missing/extra/duplicate/unsorted cases'})
    for r in rows:
        cid=r.get('case_id','');status=r.get('deletion_status');fail=lambda message:shape.append({'case_id':cid,'error':message})
        try:ss=json.loads(r['steps_json'])
        except (ValueError,KeyError,TypeError):fail('Invalid JSON');continue
        if not isinstance(ss,list):fail('Not a JSON array');continue
        if status not in ('COMPLETE','INCOMPLETE','NOT_APPLICABLE'):fail('Invalid status')
        phases={s.get('phase') for s in ss if isinstance(s,dict)}
        if status=='INCOMPLETE' and phases!=set(ORDER):plans.append({'case_id':cid,'error':'INCOMPLETE requires FINDING, REMEDIATION and VERIFICATION'})
        if status=='COMPLETE' and (not ss or phases!={'VERIFICATION'}):plans.append({'case_id':cid,'error':'COMPLETE requires nonempty verification only'})
        if status=='NOT_APPLICABLE' and ss:plans.append({'case_id':cid,'error':'NOT_APPLICABLE requires []'})
        order=[];seen=set()
        for n,s in enumerate(ss,1):
            if not isinstance(s,dict) or set(s)!=FIELDS:fail('Exact seven keys required');continue
            if type(s['step_no']) is not int or s['step_no']!=n or any(type(s[k]) is not str for k in FIELDS-{'step_no'}):fail('Wrong field type/numbering');continue
            phase=s['phase'];op=s['operation']
            if phase not in ORDER or (op,s['state']) not in ORDER.get(phase,[]):fail('Invalid phase/operation/state');continue
            key=(phase,op,s['system_id'],s['resource_id'])
            if key in seen:fail('Duplicate operation/scope')
            seen.add(key)
            if not all(key[2:]):fail('Empty scope')
            order.append((list(ORDER).index(phase),[x[0] for x in ORDER[phase]].index(op),*key[2:]))
            needs=phase=='FINDING' or status=='COMPLETE';eid=s['evidence_id']
            if needs and (not eid or sources is not None and (eid not in sources or cid in expected and time(sources[eid])>time(expected[cid]['audit_at']))):citations.append({'case_id':cid,'error':'Missing/unknown/future citation'})
            if not needs and eid:citations.append({'case_id':cid,'error':'Future work must use empty citation'})
        if order!=sorted(order):fail('Noncanonical order')
    return {'rows':len(rows),'SHAPE_VALID':'FAIL' if shape else 'PASS',
            'CITATION_REFERENCE_TIME_VALID':'FAIL' if citations else 'PASS',
            'COMPLETE_PLAN_CONTRACT_VALID':'FAIL' if shape or plans or citations else 'PASS',
            'STRICT_EVIDENCE_PROOF_VALID':'NOT VERIFIED by this independent schema/plan checker',
            'shape_errors':shape,'plan_errors':plans,'citation_errors':citations,
            'invalid_case_ids':sorted({x['case_id'] for x in shape+plans+citations})}
def main():
    root=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=root/'output.csv');p.add_argument('--dataset',type=Path,default=root/'dataset')
    p.add_argument('--requests',type=Path);p.add_argument('--report',type=Path)
    a=p.parse_args();sources={}
    for name,key,date in [('evidence_files.csv','file_id','captured_at'),('system_activity.csv','activity_id','event_time'),('user_audit_log.csv','audit_id','event_time')]:
        sources.update({r[key]:r[date] for r in read(a.dataset/name)[1]})
    result=check(a.output,a.requests or a.dataset/'deletion_requests.csv',sources)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    return 0 if result['COMPLETE_PLAN_CONTRACT_VALID']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
