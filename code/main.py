"""GhostTrace Guard CLI. Run from any directory; defaults resolve against repo root."""
import argparse
import json
from pathlib import Path
import time
from collections import Counter
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.engine import Engine
from ghosttrace.validator import validate_audit,validate_file
from ghosttrace.compiler import write_output
from ghosttrace.reviewer import GhostGuard,ReviewError
from ghosttrace.models import timestamp

ROOT=Path(__file__).resolve().parents[1]


def run(dataset,requests,output,cache_dir,allow_unresolved=False,review=True):
    start=time.perf_counter()
    corpus=Corpus(dataset)
    cases=read_csv(requests)
    index=EvidenceIndex(corpus,cache_dir)
    engine=Engine(corpus,index)
    guard=GhostGuard(corpus,index)
    audits=[]; unresolved=[]
    for case in sorted(cases,key=lambda c:c['case_id']):
        try:
            audit=engine.investigate(case)
            validate_audit(audit,corpus.sources)
            if review:
                aliases=engine.identity.aliases(timestamp(case['audit_at']))[audit.subject] if audit.subject else set()
                challenges=guard.review(audit,engine.policy,aliases)
                if challenges:
                    # One bounded recheck; unresolved disagreements remain a hard gate.
                    audit=engine.investigate(case)
                    challenges=guard.review(audit,engine.policy,aliases)
                    if challenges: raise ReviewError('; '.join(challenges))
            audits.append(audit)
        except ValueError as error:
            unresolved.append({'case_id':case['case_id'],'error':str(error)})
    if not unresolved:
        write_output(output,audits,pre_replace=lambda path:validate_file(path,cases,corpus.sources))
    metrics={'cases':len(cases),'resolved':len(audits),'unresolved':unresolved,
        'statuses':dict(Counter(a.status for a in audits)), 'runtime_seconds':time.perf_counter()-start,
        'facts':len(index.facts),'evidence_formats':dict(index.coverage),
        'reviewed_cases':guard.reviewed,'review_challenges':guard.challenges,'review_enabled':review,
        'review_unique_challenged_cases':len(guard.challenged_cases),
        'model_calls':0,'input_tokens':0,'output_tokens':0,'estimated_cost_usd':0}
    if unresolved and not allow_unresolved:
        (ROOT/'tmp').mkdir(exist_ok=True)
        (ROOT/'tmp/blocked_run_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
        raise ValueError(f'{len(unresolved)} unresolved cases; no output replaced: '+json.dumps(unresolved[:12]))
    return audits,metrics,corpus,index


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'dataset')
    parser.add_argument('--requests',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'output.csv')
    parser.add_argument('--cache-dir',type=Path,default=ROOT/'tmp/ocr')
    parser.add_argument('--no-review',action='store_true',help='Ablation only: disable independent source review')
    args=parser.parse_args()
    _,metrics,_,_=run(args.dataset,args.requests or args.dataset/'deletion_requests.csv',args.output,args.cache_dir,review=not args.no_review)
    (ROOT/'tmp').mkdir(exist_ok=True)
    (ROOT/'tmp/final_run_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2))


if __name__=='__main__':
    main()
