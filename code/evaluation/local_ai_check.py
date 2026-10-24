"""Small optional local-model benchmark; never reads sample answers or source IDs."""
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ghosttrace.ai import AIConfig,IntentAI,ollama_transport
from ghosttrace.intent import deletion_intent,AmbiguousIntent

FIXTURES=[
    ('Please put this on ice while I consider my privacy options.',None),
    ('I want every link between my identity and this service severed permanently.',True),
    ('Please explain the deletion policy for my account.',False),
    ('Delete my profile, but keep legally required invoices.',True),
]

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--model',required=True)
    parser.add_argument('--limit',type=int,default=4)
    args=parser.parse_args()
    replies=[]
    def transport(*args):
        result=ollama_transport(*args); replies.append(result); return result
    client=IntentAI(AIConfig(provider='ollama',model=args.model,max_calls=min(args.limit,4),retries=0,timeout=30,max_output_tokens=256),transport=transport)
    start=time.perf_counter(); rows=[]
    for text,expected in FIXTURES[:args.limit]:
        try: baseline=deletion_intent(text)
        except AmbiguousIntent: baseline=None
        predicted=client.classify(text)
        rows.append({'request':text,'expected':expected,'deterministic':baseline,'local_model':predicted})
    result={'provider':'Ollama loopback','requested_model':args.model,'usage':client.usage,'fixtures':rows,'replies':replies,
            'baseline_correct':sum(r['deterministic']==r['expected'] for r in rows),
            'model_correct':sum(r['local_model']==r['expected'] for r in rows),
            'runtime_seconds':time.perf_counter()-start,'billing_note':'No API fee; local electricity/hardware cost unmeasured.'}
    root=Path(__file__).resolve().parents[2]; (root/'artifacts').mkdir(exist_ok=True)
    target=root/'artifacts/local_ai_evaluation.json'
    if target.exists():
        previous=json.loads(target.read_text()); history=previous.get('previous_runs',[])
        history.append({k:v for k,v in previous.items() if k!='previous_runs'}); result['previous_runs']=history
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
