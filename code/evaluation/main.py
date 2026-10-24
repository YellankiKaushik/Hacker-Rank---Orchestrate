"""Evaluate predictions; sample references are never loaded by the engine."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import run,ROOT
from ghosttrace.loader import read_csv


def compare(audits,references):
    by_id={a.case['case_id']:a for a in audits}
    status=exact=sequence=field_matches=field_total=step_matches=pred_steps=gold_steps=evidence_matches=evidence_total=0
    failures=[]; false_complete=false_incomplete=missing_records=extra_records=missing_operations=extra_operations=0
    for reference in references:
        case_id=reference['case_id']; gold=json.loads(reference['steps_json'])
        audit=by_id.get(case_id)
        predicted=audit.steps if audit else []
        same_status=bool(audit and audit.status==reference['deletion_status'])
        false_complete+=bool(audit and audit.status=='COMPLETE' and reference['deletion_status']!='COMPLETE')
        false_incomplete+=bool(audit and audit.status=='INCOMPLETE' and reference['deletion_status']!='INCOMPLETE')
        status+=same_status
        exact+=same_status and predicted==gold
        seq=lambda ss:[(s['phase'],s['operation'],s['system_id'],s['resource_id']) for s in ss]
        sequence+=seq(predicted)==seq(gold)
        # Positional padded comparison penalizes omissions and insertions explicitly.
        for i in range(max(len(gold),len(predicted))):
            g=gold[i] if i<len(gold) else {}; p=predicted[i] if i<len(predicted) else {}
            field_total+=7
            field_matches+=sum(g.get(k,object())==p.get(k,object()) for k in ('step_no','phase','system_id','resource_id','operation','state','evidence_id'))
        canonical=lambda s:json.dumps(s,sort_keys=True)
        step_matches+=sum((Counter(map(canonical,predicted))&Counter(map(canonical,gold))).values())
        pred_steps+=len(predicted); gold_steps+=len(gold)
        expected={(s['phase'],s['operation'],s['system_id'],s['resource_id']):s for s in gold}
        actual={(s['phase'],s['operation'],s['system_id'],s['resource_id']):s for s in predicted}
        gold_resources={(s['system_id'],s['resource_id']) for s in gold}
        predicted_resources={(s['system_id'],s['resource_id']) for s in predicted}
        absent_records=sorted(gold_resources-predicted_resources); surplus_records=sorted(predicted_resources-gold_resources)
        absent_ops=sorted(expected.keys()-actual.keys()); surplus_ops=sorted(actual.keys()-expected.keys())
        missing_records+=len(absent_records); extra_records+=len(surplus_records)
        missing_operations+=len(absent_ops); extra_operations+=len(surplus_ops)
        for s in predicted:
            if s['evidence_id']:
                evidence_total+=1
                g=expected.get((s['phase'],s['operation'],s['system_id'],s['resource_id']))
                evidence_matches+=bool(g and s['evidence_id']==g['evidence_id'])
        if not same_status or predicted!=gold:
            failures.append({'case_id':case_id,'expected_status':reference['deletion_status'],
                'predicted_status':audit.status if audit else 'UNRESOLVED',
                'missing':[s for s in gold if s not in predicted],
                'extra':[s for s in predicted if s not in gold],
                'missing_records':absent_records,'extra_records':surplus_records,
                'missing_operations':absent_ops,'extra_operations':surplus_ops,
                'citation_differences':[(k,expected[k]['evidence_id'],actual[k]['evidence_id'])
                                        for k in expected.keys() & actual.keys() if expected[k]['evidence_id']!=actual[k]['evidence_id']]})
    n=len(references)
    return {'cases':n,'status_correct':status,'exact_cases':exact,'sequence_correct':sequence,
        'status_accuracy':status/n,'exact_case_rate':exact/n,'sequence_accuracy':sequence/n,
        'field_matches':field_matches,'field_total':field_total,'field_accuracy':field_matches/field_total,
        'step_matches':step_matches,'predicted_steps':pred_steps,'reference_steps':gold_steps,
        'step_precision':step_matches/pred_steps if pred_steps else 0,'step_recall':step_matches/gold_steps,
        'evidence_reference_matches':evidence_matches,'evidence_reference_total':evidence_total,
        'false_complete':false_complete,'false_incomplete':false_incomplete,
        'unresolved_cases':len(references)-len(by_id),'missing_records':missing_records,'extra_records':extra_records,
        'missing_operations':missing_operations,'extra_operations':extra_operations,
        'failures':failures}


if __name__=='__main__':
    audits,run_metrics,_,_=run(ROOT/'dataset',ROOT/'dataset/sample_deletion_requests.csv',
        ROOT/'tmp/sample_predictions.csv',ROOT/'tmp/ocr',True)
    metrics=compare(audits,read_csv(ROOT/'dataset/sample_output.csv'))
    metrics['run']=run_metrics
    (ROOT/'tmp').mkdir(exist_ok=True)
    (ROOT/'tmp/sample_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('failures','run')},indent=2))
    print('unresolved',run_metrics['unresolved'])
