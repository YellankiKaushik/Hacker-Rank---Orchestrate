"""Execute measured Phase 2 gates; keeps official-plan failures explicit."""
import sys,subprocess,json,os,hashlib,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import run
from ghosttrace.compiler import write_output
from ghosttrace.loader import read_csv,Corpus
from validate_candidate import validate
from independent_contract import check
from evaluation.independent_score import read,score

ROOT=Path(__file__).resolve().parents[2]
def execute():
    r=ROOT;t=r/'tmp/phase2-verification';t.mkdir(exist_ok=True)
    tests=subprocess.run([sys.executable,'-B','-X','utf8','-m','unittest','discover','-s','code/tests','-q'],cwd=r,capture_output=True,text=True)
    (t/'tests.txt').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    if tests.returncode:raise RuntimeError('Phase 2 regression failure: '+tests.stderr)
    samples={}
    for mode,review in [('primary',False),('strict',True),('candidate',True)]:
        audits,m,_,_=run(r/'dataset',r/'dataset/sample_deletion_requests.csv',t/(mode+'.csv'),r/'tmp/ocr',True,review,False,'candidate' if mode=='candidate' else 'strict',t/(mode+'-uncertainty.md'))
        # Unresolved strict/primary runs intentionally do not write a complete
        # output. Serialize accepted subsets solely for the independent scorer.
        if mode!='candidate':write_output(t/(mode+'.csv'),audits)
        samples[mode]={'rows':read(t/(mode+'.csv')),'runtime_seconds':m['runtime_seconds'],'unresolved':len(m['unresolved'])}
    references=read(r/'dataset/sample_output.csv') # after every inference variant
    for variant in samples.values():variant['independent_metrics']=score(variant.pop('rows'),references)
    processes=[]
    for n in (19,41):
        output=t/f'full-{n}.csv';metrics=t/f'full-{n}.json'
        p=subprocess.run([sys.executable,'-B','-X','utf8','code/main.py','--mode','candidate','--output',str(output),'--metrics-path',str(metrics),'--uncertainty-report',str(t/f'uncertainty-{n}.md')],cwd=r,env={**os.environ,'PYTHONHASHSEED':str(n)},capture_output=True,text=True,timeout=60)
        if p.returncode:raise RuntimeError(p.stderr)
        processes.append({'seed':n,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'metrics':json.loads(metrics.read_text())})
    expected=hashlib.sha256((r/'output.csv').read_bytes()).hexdigest()
    assert all(v['sha256']==expected for v in processes)
    cases=read_csv(r/'dataset/deletion_requests.csv');c=Corpus(r/'dataset')
    emitted=validate(r/'output.csv',cases,c,r/'tmp/ocr')
    contract=check(r/'output.csv',r/'dataset/deletion_requests.csv',{k:v.isoformat() for k,v in c.sources.items()})
    strictout=t/'strict-full.csv'
    p=subprocess.run([sys.executable,'-B','-X','utf8','code/main.py','--output',str(strictout)],cwd=r,capture_output=True,text=True,timeout=60)
    assert p.returncode!=0 and not strictout.exists()
    m=processes[0]['metrics']
    result={'tests':{'passed':int(re.search(r'Ran (\d+) tests',tests.stderr)[1]),'failed':0,'skipped':0},
       'sample_variants':samples,'fresh_processes':[{'seed':x['seed'],'sha256':x['sha256'],'runtime_seconds':x['metrics']['runtime_seconds']} for x in processes],
       'candidate_rows':m['resolved'],'statuses':m['statuses'],'strict_accepted':m['strict_resolved'],
       'uncertain_complete':sum(v['status']=='COMPLETE' for v in m['uncertain_cases']),
       'uncertain_incomplete':sum(v['status']=='INCOMPLETE' for v in m['uncertain_cases']),
       'independent_contract':contract,'emitted_claim_checks':emitted,'strict_cli_expected_block':True,
       'model_usage':{k:m[k] for k in ('model_calls','input_tokens','output_tokens','estimated_cost_usd')},
       'classification':'C — candidate contains confirmed incomplete plans; not fully contract-compliant'}
    (r/'artifacts/phase2-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('sample_variants','emitted_claim_checks')},indent=2))
    return result
if __name__=='__main__':execute()
