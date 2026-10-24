"""Verify reproducibility, source semantics and source ZIP; never submits artifacts."""
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import uuid
import zipfile
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.semantic_validation import validate_semantic_file

ROOT=Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def secret_scan(archive):
    pattern=re.compile(rb'sk-[A-Za-z0-9_-]{25,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    configured=[v.encode() for k,v in os.environ.items() if re.search(r'(?:API_KEY|ACCESS_TOKEN|SECRET_KEY)$',k) and len(v)>=12]
    findings=[]
    with zipfile.ZipFile(archive) as package:
        for name in package.namelist():
            body=package.read(name)
            if pattern.search(body) or any(value in body for value in configured): findings.append(name)
    return findings


def main():
    result={'run_id':str(uuid.uuid4()),'timestamp_utc':datetime.now(timezone.utc).isoformat(),'gates':{}}
    gates=result['gates']
    result['dependencies']={'python':sys.version.split()[0],'pypdf':importlib.metadata.version('pypdf'),'sqlite':sqlite3.sqlite_version}
    gates['local_dependency_imports']='PASS'; gates['isolated_fresh_dependency_install']='NOT VERIFIED'
    tests=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','code/tests','-q'],cwd=ROOT,capture_output=True,text=True,timeout=30)
    match=re.search(r'Ran (\d+) tests',tests.stdout+tests.stderr)
    result['tests']=int(match[1]) if match else None
    gates['unit_and_synthetic_integration_tests']='PASS' if tests.returncode==0 else 'FAIL'
    if tests.returncode: raise RuntimeError('Regression tests failed')
    temp=ROOT/'tmp'/('release-'+result['run_id']); temp.mkdir(parents=True)
    if not temp.resolve().is_relative_to((ROOT/'tmp').resolve()): raise ValueError('Release path escaped workspace')
    runs=[]
    for n,seed in enumerate(('19','41')):
        directory=temp/f'process-{n+1}'; metrics=directory/'metrics.json'
        process=subprocess.run([sys.executable,'-X','utf8','code/diagnostics.py',
            '--artifact-dir',str(directory),'--metrics-path',str(metrics)],cwd=ROOT,
            env={**os.environ,'PYTHONHASHSEED':seed},capture_output=True,text=True,timeout=60)
        if process.returncode: raise RuntimeError('Fresh-process diagnostics failed: '+process.stderr[-1000:])
        measured=json.loads(metrics.read_text())
        runs.append({'seed':seed,'rows':measured['resolved'],'unresolved':len(measured['unresolved']),
                     'sha256':sha(directory/'resolved_predictions.partial.csv'),'runtime_seconds':measured['runtime_seconds']})
    expected=sha(ROOT/'artifacts/resolved_predictions.partial.csv')
    result['fresh_processes']=runs; result['partial_sha256']=expected
    gates['fresh_process_reproducibility']='PASS' if all(r['sha256']==expected for r in runs) else 'FAIL'
    if gates['fresh_process_reproducibility']=='FAIL': raise RuntimeError('Fresh-process output differs')
    corpus=Corpus(ROOT/'dataset'); rows=read_csv(ROOT/'artifacts/resolved_predictions.partial.csv')
    ids={r['case_id'] for r in rows}
    subset=[c for c in read_csv(ROOT/'dataset/deletion_requests.csv') if c['case_id'] in ids]
    result['partial_semantically_validated_rows']=validate_semantic_file(
        ROOT/'artifacts/resolved_predictions.partial.csv',subset,corpus,ROOT/'tmp/ocr')
    gates['partial_artifact_source_semantics']='PASS'
    full=subprocess.run([sys.executable,'-X','utf8','code/validate_output.py'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    gates['final_518_row_output']='PASS' if full.returncode==0 else 'FAIL'
    result['final_output_blocker']='No supported 518-row output exists; unresolved cases are withheld' if full.returncode else ''
    official=subprocess.run(['git','diff','--exit-code','acb3dfc','--','dataset','AGENTS.md','problem_statement.md','agent_trace_instructions.md'],cwd=ROOT,capture_output=True,text=True)
    gates['official_data_and_instructions_unchanged']='PASS' if official.returncode==0 else 'FAIL'
    packaging=subprocess.run([sys.executable,'-X','utf8','code/package_submission.py'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    if packaging.returncode: raise RuntimeError('Package extraction/check failed: '+packaging.stderr[-1000:])
    result['package']=json.loads((ROOT/'artifacts/package_verification.json').read_text())
    gates['zip_structure_and_clean_extraction']='PASS'
    findings=secret_scan(ROOT/'code.zip')
    gates['basic_archive_secret_scan']='FAIL' if findings else 'PASS'
    result['secret_scan_findings_paths_only']=findings
    gates['live_model_availability_and_quality']='NOT VERIFIED'
    result['ai_blocker']='Read-only provider check returned HTTP 401; no live inference was performed'
    gates['append_only_transcript_exists']='PASS' if (ROOT/'log.txt').exists() else 'FAIL'
    gates['final_closed_session_trace_zip']='NOT VERIFIED'
    required=('unit_and_synthetic_integration_tests','fresh_process_reproducibility','partial_artifact_source_semantics',
        'final_518_row_output','official_data_and_instructions_unchanged','zip_structure_and_clean_extraction','basic_archive_secret_scan')
    result['submission_ready']=all(gates[k]=='PASS' for k in required)
    result['limitations']=[
        'Code ZIP is a development checkpoint; extraction success does not waive missing final predictions.',
        'Dependency imports use the bundled runtime; a fresh dependency installation was not tested.',
        'Semantic checks re-read sources but share domain adapters/policy; no hidden-answer oracle exists.',
        'Basic secret scanning is not a complete privacy audit; raw session traces are excluded from the ZIP.',
        'The active session must finish and the app close before final trace copying/redaction/packaging.',
        'No HackerRank upload or interview was performed.']
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    (artifacts/'release_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    report='# Release readiness — measured gates\n\n'
    report+=f"Run `{result['run_id']}` at {result['timestamp_utc']}. **Submission ready: {result['submission_ready']}.**\n\n| Gate | Result |\n|---|---|\n"
    report+=''.join(f'| {k} | {v} |\n' for k,v in gates.items())
    report+=f"\nTests: {result['tests']}. Accepted rows semantically revalidated: {result['partial_semantically_validated_rows']}. Partial SHA-256: `{expected}`.\n\n"
    report+=f"Fresh processes: `{runs}`.\n\nPackage SHA-256: `{result['package']['sha256']}`; bytes: {result['package']['bytes']}.\n\n"
    report+='\n'.join('- '+v for v in result['limitations'])+'\n'
    (artifacts/'READINESS.md').write_text(report,encoding='utf-8')
    print(json.dumps({'gates':gates,'tests':result['tests'],'rows':len(rows),
        'partial_sha256':expected,'package_sha256':result['package']['sha256'],'submission_ready':result['submission_ready']},indent=2))


if __name__=='__main__': main()
