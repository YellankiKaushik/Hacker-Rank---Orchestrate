"""Validate candidate shape and emitted source claims; report strict uncertainty separately."""
import argparse
import hashlib
import json
from pathlib import Path
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.engine import Engine
from ghosttrace.models import Audit,timestamp
from ghosttrace.candidate import validate_candidate_file,validate_emitted_sources
from ghosttrace.intent_resolution import IntentResolution
from ghosttrace.reviewer import GhostGuard

ROOT=Path(__file__).resolve().parents[1]


def validate(path,cases,corpus,cache,intent_resolutions=None):
    count=validate_candidate_file(path,cases,corpus.sources,intent_resolutions)
    index=EvidenceIndex(corpus,cache); engine=Engine(corpus,index); guard=GhostGuard(corpus,index)
    rows={r['case_id']:r for r in read_csv(path)}
    cited=0; unproven=[]; strict=0
    for case in cases:
        # Revalidate contextual intent; never trust serialized sidecar decisions alone.
        resolution=(intent_resolutions or {}).get(case['case_id'])
        if resolution:
            from ghosttrace.intent_resolution import validated_decision
            from types import SimpleNamespace
            validated_decision(case['request_text'],resolution)
            engine.intent_ai=SimpleNamespace(classify=lambda text,r=resolution:r.decision,last_result={'quote':resolution.quote})
        else: engine.intent_ai=None
        expected=engine.investigate(case,permit_partial=True)
        row=rows[case['case_id']]
        submitted=Audit(case,expected.subject,expected.facts,row['deletion_status'],json.loads(row['steps_json']),
                        expected.issues,expected.bindings,intent_resolution=expected.intent_resolution)
        if submitted.status!=expected.status or submitted.steps!=expected.steps:
            raise ValueError(f'{case["case_id"]}: artifact differs from source-grounded candidate policy/complete known operations')
        aliases=engine.identity.aliases(timestamp(case['audit_at'])).get(expected.subject,set())
        cited+=validate_emitted_sources(submitted,guard,engine.policy,aliases)
        try: issues=guard.review(submitted,engine.policy,aliases)
        except ValueError as error: issues=[str(error)]
        if issues or any(v.startswith(('Unresolved state:','Linked resource has no admissible state:','No admissible')) for v in expected.issues):
            unproven.append(case['case_id'])
        else: strict+=1
    return {'rows':count,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'CSV_SCHEMA_VALIDITY':'PASS','CITATION_INTEGRITY':'PASS','TEMPORAL_VALIDITY':'PASS',
            'POLICY_VALIDITY':'PASS','SOURCE_PROVENANCE':'PASS',
            'SEMANTIC_CERTAINTY':'FAIL' if unproven else 'PASS',
            'source_backed_cited_steps':cited,'total_cited_steps':cited,
            'strict_accepted':strict,'uncertain_cases':unproven,'fabricated_source_references':0,
            'limitation':'PASS covers emitted claims/known operations; unobserved obligations remain unproven. Shared adapters/policy are not a hidden-answer oracle.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'dataset')
    parser.add_argument('--requests',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'output.csv')
    parser.add_argument('--cache-dir',type=Path,default=ROOT/'tmp/ocr')
    parser.add_argument('--report',type=Path,default=ROOT/'artifacts/candidate_validation.json')
    parser.add_argument('--intent-resolutions',type=Path,help='Optional internal provenance sidecar; independently checked against each request')
    args=parser.parse_args()
    resolutions={k:IntentResolution(**v) for k,v in json.loads(args.intent_resolutions.read_text()).items()} if args.intent_resolutions else None
    result=validate(args.output,read_csv(args.requests or args.dataset/'deletion_requests.csv'),Corpus(args.dataset),args.cache_dir,resolutions)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='uncertain_cases'},indent=2))
    print(f"Uncertain cases: {len(result['uncertain_cases'])}. This command does not waive strict semantic validation.")


if __name__=='__main__': main()
