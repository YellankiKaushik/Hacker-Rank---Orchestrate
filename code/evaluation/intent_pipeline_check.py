"""Optional two-call loopback experiment of intent provenance through export/review."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ghosttrace.ai import AIConfig,IntentAI
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.engine import Engine
from ghosttrace.reviewer import GhostGuard
from ghosttrace.compiler import write_output
from ghosttrace.candidate import validate_candidate_file
from ghosttrace.models import timestamp
from validate_candidate import validate


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--model',required=True)
    args=parser.parse_args(); root=Path(__file__).resolve().parents[2]
    client=IntentAI(AIConfig(provider='ollama',model=args.model,max_calls=2,retries=0,timeout=30,max_output_tokens=256))
    outcomes=[]; start=time.perf_counter()
    for text,wanted in [('I want every link between my identity and this service severed permanently.',True),
                        ('Please suspend my account temporarily.',False)]:
        with tempfile.TemporaryDirectory(dir=root/'tmp/tests') as d:
            folder=Path(d); early='2026-01-01T00:00:00Z'
            (folder/'source.json').write_text(json.dumps({'records':[{'recorded_at':early,'system':'account_service',
                'resource_id':'fixture_profile','record_type':'USER_PROFILE','result':'NOT_FOUND','subject_reference':'fixture_subject'}]}))
            corpus=SimpleNamespace(root=folder,manifest=[{'file_id':'fixture_source','file_path':'source.json','captured_at':early}],
                sources={'fixture_source':timestamp(early)},identities=[{'user_id':'fixture_subject','name':'Fixture','email':'fixture@example.test',
                'phone':'','email_hash':'','updated_at':early}],history=[],activities=[],rules=[{
                    'data_category':'USER_PROFILE','required_action':'DELETE','condition':'Always'}])
            case={'case_id':'fixture','email':'fixture@example.test','request_text':text,'audit_at':'2026-06-01T00:00:00Z'}
            try:
                index=EvidenceIndex(corpus); engine=Engine(corpus,index,client); audit=engine.investigate(case)
                guard=GhostGuard(corpus,index); issues=guard.review(audit,engine.policy,{'fixture_subject'} if wanted else set())
                if issues: raise ValueError('; '.join(issues))
                resolutions={'fixture':audit.intent_resolution}; output=folder/'output.csv'
                write_output(output,[audit],pre_replace=lambda p:validate_candidate_file(p,[case],corpus.sources,resolutions))
                validate(output,[case],corpus,None,resolutions)
                outcomes.append({'expected_deletion':wanted,'decision':audit.intent_resolution.decision,
                    'method':audit.intent_resolution.method,'validation':audit.intent_resolution.validation,'export_and_fresh_validation':'PASS'})
            except ValueError as error:
                outcomes.append({'expected_deletion':wanted,'export_and_fresh_validation':'REJECTED','error_type':type(error).__name__})
    result={'requested_model':args.model,'provider':'ollama loopback','fixtures':outcomes,'usage':client.usage,
        'seconds':time.perf_counter()-start,'accepted':sum(r['export_and_fresh_validation']=='PASS' for r in outcomes),
        'limitation':'Two authored fixtures, no dataset accuracy claim; no mock usage included. Final inference remains separately measured.'}
    (root/'artifacts/intent_pipeline_evaluation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
