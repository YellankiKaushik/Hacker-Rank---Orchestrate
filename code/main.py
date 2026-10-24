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
from ghosttrace.reviewer import GhostGuard,ReviewError,rejection_category
from ghosttrace.models import timestamp
from ghosttrace.ai import IntentAI
from ghosttrace.candidate import validate_candidate_file,validate_candidate_audit,validate_emitted_sources,uncertainty,write_uncertainty

ROOT=Path(__file__).resolve().parents[1]


def run(dataset,requests,output,cache_dir,allow_unresolved=False,review=True,ai=False,mode='strict',uncertainty_path=None):
    if mode not in ('strict','candidate'): raise ValueError('Unknown execution mode')
    if mode=='candidate' and not review: raise ValueError('Candidate requires source review')
    start=time.perf_counter()
    corpus=Corpus(dataset)
    cases=read_csv(requests)
    index=EvidenceIndex(corpus,cache_dir)
    intent_ai=IntentAI(cache_dir=Path(cache_dir).parent/'ai') if ai else None
    engine=Engine(corpus,index,intent_ai=intent_ai)
    guard=GhostGuard(corpus,index)
    audits=[]; unresolved=[]; case_diagnostics=[]; uncertain=[]; cited_steps=0; strict_resolved=0
    for case in sorted(cases,key=lambda c:c['case_id']):
        detail={'case_id':case['case_id'],'primary_status':None,'rejections':[],
                'reinvestigation_sources':[],'review_rounds':0,'contradictions':[]}
        try:
            audit=engine.investigate(case)
            detail['primary_status']=audit.status
            detail['contradictions']=[v for v in audit.issues if v.startswith('Conflicting')]
            validate_audit(audit,corpus.sources)
            if review:
                aliases=engine.identity.aliases(timestamp(case['audit_at']))[audit.subject] if audit.subject else set()
                challenges=guard.review(audit,engine.policy,aliases)
                detail['review_rounds']=1
                if challenges:
                    detail['rejections']=[{'category':rejection_category(c),'message':c} for c in challenges]
                    audit,retrieved,sources=engine.reinvestigate(case,audit)
                    detail['reinvestigation_sources']=sources
                    guard.refresh(retrieved)
                    challenges=guard.review(audit,engine.policy,aliases)
                    detail['review_rounds']=2
                    if challenges: raise ReviewError('; '.join(challenges))
            if mode=='candidate': cited_steps+=validate_emitted_sources(audit,guard,engine.policy,aliases)
            audits.append(audit)
            strict_resolved+=1
            detail['accepted']=True
        except ValueError as error:
            unresolved.append({'case_id':case['case_id'],'error':str(error),'category':rejection_category(str(error))})
            detail['accepted']=False
            detail['final_error']=str(error)
            if mode=='candidate':
                audit=engine.investigate(case,permit_partial=True)
                aliases=engine.identity.aliases(timestamp(case['audit_at'])).get(audit.subject,set())
                validate_candidate_audit(audit,corpus.sources)
                cited_steps+=validate_emitted_sources(audit,guard,engine.policy,aliases)
                uncertain.append(uncertainty(case,audit,error,guard,engine.policy,aliases))
                audits.append(audit)
                detail['candidate_status']=audit.status
        case_diagnostics.append(detail)
    if not unresolved or mode=='candidate':
        validator=validate_candidate_file if mode=='candidate' else validate_file
        write_output(output,audits,pre_replace=lambda path:validator(path,cases,corpus.sources))
    metrics={'cases':len(cases),'resolved':len(audits),'unresolved':unresolved,
        'statuses':dict(Counter(a.status for a in audits)), 'runtime_seconds':time.perf_counter()-start,
        'facts':len(index.facts),'evidence_formats':dict(index.coverage),
        'reviewed_cases':guard.reviewed,'review_challenges':guard.challenges,'review_enabled':review,
        'review_unique_challenged_cases':len(guard.challenged_cases),
        'case_diagnostics':case_diagnostics,
        'rejection_categories':dict(Counter(u['category'] for u in unresolved)),
        'targeted_source_reads':engine.source_reads,'targeted_source_cache_hits':engine.source_cache_hits,
        'model_calls':0,'input_tokens':0,'output_tokens':0,'estimated_cost_usd':0}
    metrics.update(mode=mode,strict_resolved=strict_resolved,uncertain_cases=uncertain,
                   source_backed_cited_steps=cited_steps,unsupported_status_inferences=len(uncertain),
                   fabricated_source_references=0)
    if mode=='candidate':
        metrics['structural_validation']='PASS'
        metrics['semantic_certainty']='FAIL' if uncertain else 'PASS'
        write_uncertainty(uncertainty_path or Path(output).parent/'artifacts/SUBMISSION_UNCERTAINTY_REPORT.md',metrics)
    if intent_ai:
        metrics['ai_usage']=intent_ai.usage
        metrics['model_calls']=intent_ai.usage['attempts']
        for field in ('input_tokens','output_tokens','estimated_cost_usd'):
            metrics[field]=intent_ai.usage[field]
        metrics['ai_disabled_reason']=intent_ai.disabled_reason or ('missing model/credential/pricing configuration' if not intent_ai.ready() else '')
    if unresolved and not allow_unresolved and mode=='strict':
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
    parser.add_argument('--ai',action='store_true',help='Opt-in bounded ambiguous-intent interpretation; requires environment configuration')
    parser.add_argument('--mode',choices=('strict','candidate'),default='strict',help='Strict audit (default), or explicitly uncertain submission prediction')
    parser.add_argument('--uncertainty-report',type=Path)
    parser.add_argument('--metrics-path',type=Path)
    args=parser.parse_args()
    _,metrics,_,_=run(args.dataset,args.requests or args.dataset/'deletion_requests.csv',args.output,args.cache_dir,review=not args.no_review,ai=args.ai,mode=args.mode,uncertainty_path=args.uncertainty_report)
    (ROOT/'tmp').mkdir(exist_ok=True)
    metrics_path=args.metrics_path or ROOT/f'tmp/{args.mode}_run_metrics.json'
    metrics_path.parent.mkdir(parents=True,exist_ok=True)
    metrics_path.write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('case_diagnostics','uncertain_cases','unresolved')},indent=2))


if __name__=='__main__':
    main()
