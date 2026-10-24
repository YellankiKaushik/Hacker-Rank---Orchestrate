import csv
import json
import os
from pathlib import Path
import tempfile

OPERATIONS = {
    'FINDING': {'REPORT_REMAINING_RECORD':'PRESENT','REPORT_EXPOSED_PII':'PRESENT',
                'REPORT_ACTIVE_DATA_FLOW':'ACTIVE','REPORT_RESTORE_RISK':'ACTIVE'},
    'REMEDIATION': {'DISABLE_DATA_FLOW':'DISABLED','BLOCK_RESTORE':'BLOCKED','DELETE_RECORD':'ABSENT',
                    'REDACT_RECORD':'REDACTED','ANONYMIZE_RECORD':'ANONYMIZED'},
    'VERIFICATION': {'VERIFY_RECORD_ABSENT':'ABSENT','VERIFY_RECORD_PRESENT':'PRESENT',
                     'VERIFY_RECORD_REDACTED':'REDACTED','VERIFY_RECORD_ANONYMIZED':'ANONYMIZED',
                     'VERIFY_DATA_FLOW_DISABLED':'DISABLED','VERIFY_RESTORE_BLOCKED':'BLOCKED'},
}
FIELDS = {'step_no','phase','system_id','resource_id','operation','state','evidence_id'}
HEADER = ['case_id','deletion_status','steps_json']


def sort_key(step):
    return (list(OPERATIONS).index(step['phase']),list(OPERATIONS[step['phase']]).index(step['operation']),step['system_id'],step['resource_id'])


def make_step(phase,operation,fact,evidence=''):
    return {'step_no':0,'phase':phase,'system_id':fact.system,'resource_id':fact.resource,
            'operation':operation,'state':OPERATIONS[phase][operation],'evidence_id':evidence}


def compile_steps(facts, policy, cutoff):
    violations = [f for f in facts if policy.violation(f,cutoff)]
    status = 'INCOMPLETE' if violations else 'COMPLETE'
    steps = []
    for fact in facts:
        finding,remediation,verification = policy.operations(fact,cutoff)
        if policy.violation(fact,cutoff):
            if not finding:
                raise ValueError('Required retained record is missing; contract has no restore-required operation')
            steps.extend([make_step('FINDING',finding,fact,fact.source),make_step('REMEDIATION',remediation,fact)])
        # An absent optional redaction/anonymization record is verified as absent, not present.
        if fact.state=='ABSENT' and verification in ('VERIFY_RECORD_REDACTED','VERIFY_RECORD_ANONYMIZED'):
            verification='VERIFY_RECORD_ABSENT'
        steps.append(make_step('VERIFICATION',verification,fact,fact.source if status=='COMPLETE' else ''))
    steps.sort(key=sort_key)
    for n,step in enumerate(steps,1): step['step_no']=n
    return status,steps


def write_output(path, audits, pre_replace=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd,temp = tempfile.mkstemp(prefix='.ghosttrace-',suffix='.csv',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=HEADER,lineterminator='\n')
            writer.writeheader()
            for audit in sorted(audits,key=lambda a:a.case['case_id']):
                writer.writerow({'case_id':audit.case['case_id'],'deletion_status':audit.status,
                                 'steps_json':json.dumps(audit.steps,ensure_ascii=False,separators=(',',':'))})
        if pre_replace:
            pre_replace(Path(temp))
        os.replace(temp,path)
    finally:
        if os.path.exists(temp): os.unlink(temp)
