"""Write explicitly partial predictions and issue reports without replacing output.csv."""
from pathlib import Path
import json
import hashlib
import time
from main import run,ROOT
from ghosttrace.compiler import write_output
from ghosttrace.validator import validate_file
from ghosttrace.loader import read_csv


def generate():
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    audits,metrics,corpus,index=run(ROOT/'dataset',ROOT/'dataset/deletion_requests.csv',
        ROOT/'output.csv',ROOT/'tmp/ocr',allow_unresolved=True)
    partial=artifacts/'resolved_predictions.partial.csv'
    cases=[a.case for a in audits]
    write_output(partial,audits,pre_replace=lambda path:validate_file(path,cases,corpus.sources))
    metrics['partial_output_sha256']=hashlib.sha256(partial.read_bytes()).hexdigest()
    metrics['submission_ready']=not bool(metrics['unresolved'])
    metrics['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'dataset').glob('*.csv')) if p.name!='sample_output.csv'}
    (ROOT/'tmp/final_run_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    (artifacts/'run_diagnostics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('input_sha256','unresolved')},indent=2))
    print(f'Unresolved: {len(metrics["unresolved"])}; see code/docs/UNRESOLVED_ISSUES.md after report generation.')
    return metrics


if __name__=='__main__': generate()
