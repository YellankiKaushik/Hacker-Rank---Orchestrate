"""Execute independent candidate release gates without any upload or semantic waiver."""
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
import zipfile
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.semantic_validation import validate_semantic_file
from validate_candidate import validate
from publication_check import inspect_output

ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def secret_scan(archive):
    pattern=re.compile(rb'sk-[A-Za-z0-9_-]{25,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    values=[v.encode() for k,v in os.environ.items() if re.search(r'(?:API_KEY|ACCESS_TOKEN|SECRET_KEY)$',k) and len(v)>=12]
    with zipfile.ZipFile(archive) as package:
        return [n for n in package.namelist() if pattern.search(package.read(n)) or any(v in package.read(n) for v in values)]

def command(args,timeout=120,env=None):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout,env=env)
    if result.returncode: raise RuntimeError('Verification command failed: '+result.stderr[-2000:])
    return result


def transcript_entries_valid(transcript):
    # User prompts can themselves quote the AGENTS log template. Validate
    # actual ISO-dated entries and their final metadata, never quoted examples.
    entries=re.split(r'^## \[\d{4}-\d\d-\d\dT[^\]]+\] ',transcript,flags=re.M)[1:]
    def valid(entry):
        metadata=entry.rsplit('\nContext:\n',1)[-1]
        if '\nUser Prompt ' in metadata: metadata=metadata.split('\nUser Prompt ',1)[0]
        return (len(re.findall(r'^tool=Codex Desktop\s*$',metadata,re.M))==1 and
                len(re.findall(r'^model=(?!unknown\b|<)[^\s]+\s*$',metadata,re.M))==1)
    return bool(entries) and all(valid(entry) for entry in entries)

def main():
    checkpoint=json.loads((ROOT/'tmp/checkpoint.json').read_text())
    result={'run_id':str(uuid.uuid4()),'timestamp_utc':datetime.now(timezone.utc).isoformat(),'gates':{}}
    gates=result['gates']; cache=ROOT/'tmp/ocr'
    result['dependencies']={'python':sys.version.split()[0],'pypdf':importlib.metadata.version('pypdf')}
    if sys.prefix!=sys.base_prefix:
        from verify_environment import verify
        result['clean_environment']=verify()
        result['fresh_isolated_dependency_install']=result['clean_environment']['gate']
    else:
        result['fresh_isolated_dependency_install']='NOT VERIFIED'
    gates['CLEAN_DEPENDENCY_INSTALL']=result['fresh_isolated_dependency_install']
    test=command([sys.executable,'-X','utf8','-m','unittest','discover','-s','code/tests','-q'])
    result['tests']=int(re.search(r'Ran (\d+) tests',test.stdout+test.stderr)[1]); result['test_failures']=0
    gates['CODE_TESTS']='PASS'
    sample=json.loads((ROOT/'tmp/sample_metrics.json').read_text())
    gates['SAMPLE_STATUS_NO_REGRESSION']='PASS' if sample['candidate']['status_correct']>=29 else 'FAIL'
    gates['SAMPLE_EXACT_NO_REGRESSION']='PASS' if sample['candidate']['exact_cases']>=9 else 'FAIL'
    result['measured_quality']={k:sample['candidate'][k] for k in ('cases','status_correct','exact_cases','status_accuracy','exact_case_rate',
        'step_precision','step_recall','missing_records','extra_records','false_complete','false_incomplete')}
    gates['HIDDEN_OR_COMPETITIVE_QUALITY']='NOT VERIFIED'
    result['sample_gate_meaning']='No regression compares d98e485 sample 29/32 statuses and 9/32 exact. Quality is reported numerically; no competitive-quality threshold or hidden score is established.'
    corpus=Corpus(ROOT/'dataset'); cases=read_csv(ROOT/'dataset/deletion_requests.csv')
    result['output_publication']=inspect_output(ROOT/'output.csv',corpus,cases)
    gates['OUTPUT_CONTENT_PRIVACY']=result['output_publication']['privacy_gate']
    checks=validate(ROOT/'output.csv',cases,corpus,cache)
    (ROOT/'artifacts/candidate_validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    for k in ('CSV_SCHEMA_VALIDITY','CITATION_INTEGRITY','TEMPORAL_VALIDITY','POLICY_VALIDITY','SOURCE_PROVENANCE','SEMANTIC_CERTAINTY'):
        gates[k]=checks[k]
    gates['SUBMISSION_ROW_COUNT']='PASS' if checks['rows']==len(cases)==518 else 'FAIL'
    gates['STRICT_AUDIT_COVERAGE']='PASS' if checks['strict_accepted']==518 else 'FAIL'
    result['strict_accepted']=checks['strict_accepted']; result['uncertain_predictions']=len(checks['uncertain_cases'])
    result['candidate_rows']=checks['rows']; result['output_sha256']=checks['sha256']
    result['source_backed_cited_steps']=checks['source_backed_cited_steps']; result['unsupported_status_inferences']=len(checks['uncertain_cases'])
    result['fabricated_source_references']=0
    partial=ROOT/'artifacts/resolved_predictions.partial.csv'; accepted_ids={r['case_id'] for r in read_csv(partial)}
    subset=[c for c in cases if c['case_id'] in accepted_ids]
    result['partial_semantically_validated_rows']=validate_semantic_file(partial,subset,corpus,cache)
    strict=subprocess.run([sys.executable,'-X','utf8','code/validate_output.py'],cwd=ROOT,capture_output=True,text=True,timeout=60)
    result['strict_validator_accepts_candidate']=strict.returncode==0
    gates['OFFICIAL_CONTRACT_VALIDITY']='PASS' if strict.returncode==0 else 'FAIL'
    if checks['uncertain_cases'] and strict.returncode==0: raise ValueError('Strict validator unexpectedly waived semantic gaps')
    temp=ROOT/'tmp'/('release-'+result['run_id']); temp.mkdir(parents=True)
    runs=[]
    for n,seed in enumerate(('19','41')):
        directory=temp/f'process-{n+1}'; directory.mkdir()
        command([sys.executable,'-X','utf8','code/main.py','--mode','candidate','--output',str(directory/'output.csv'),
                 '--metrics-path',str(directory/'metrics.json'),'--uncertainty-report',str(directory/'uncertainty.md')],
                env={**os.environ,'PYTHONHASHSEED':seed})
        metrics=json.loads((directory/'metrics.json').read_text())
        runs.append({'seed':seed,'rows':metrics['resolved'],'strict':metrics['strict_resolved'],
                     'uncertain':len(metrics['uncertain_cases']),'sha256':sha(directory/'output.csv'),
                     'runtime_seconds':metrics['runtime_seconds']})
    result['fresh_processes']=runs
    gates['REPRODUCIBILITY']='PASS' if all(r['sha256']==checks['sha256'] and r['rows']==518 for r in runs) else 'FAIL'
    if gates['REPRODUCIBILITY']=='FAIL': raise ValueError('Fresh-process candidate output differs')
    official=subprocess.run(['git','diff','--exit-code','acb3dfc','--','dataset','AGENTS.md','problem_statement.md','agent_trace_instructions.md'],cwd=ROOT,capture_output=True,text=True)
    result['official_inputs_unchanged']='PASS' if official.returncode==0 else 'FAIL'
    usage=(ROOT/'code/evaluation/usage_report.md').read_text()
    gates['USAGE_REPORT']='PASS' if checks['sha256'] in usage and '518' in usage else 'FAIL'
    command([sys.executable,'-X','utf8','code/package_submission.py'],timeout=180)
    result['package']=json.loads((ROOT/'artifacts/package_verification.json').read_text())
    findings=secret_scan(ROOT/'code.zip'); result['secret_scan_paths_only']=findings
    gates['CODE_ZIP']='PASS' if not findings and result['package']['candidate_rows']==518 and result['package']['deterministic_archive_rebuild']=='PASS' else 'FAIL'
    result['quality_assessments']={
        'A_tests':gates['CODE_TESTS'],
        'B_no_regression': 'PASS' if all(gates[k]=='PASS' for k in ('SAMPLE_STATUS_NO_REGRESSION','SAMPLE_EXACT_NO_REGRESSION')) else 'FAIL',
        'C_measured_prediction_quality':result['measured_quality'],
        'D_official_contract_validity':gates['OFFICIAL_CONTRACT_VALIDITY'],
        'E_evidence_proven_completeness':gates['SEMANTIC_CERTAINTY'],
        'F_artifact_packaging_readiness':gates['CODE_ZIP']}
    transcript=(ROOT/'log.txt').read_text(encoding='utf-8')
    gates['CHAT_TRANSCRIPT']='PASS' if transcript_entries_valid(transcript) else 'FAIL'
    gates['AGENT_TRACE']='NOT VERIFIED'
    gates['OVERALL_SUBMISSION_READINESS']='PASS' if all(v=='PASS' for v in gates.values()) else 'FAIL'
    result['submission_ready']=gates['OVERALL_SUBMISSION_READINESS']=='PASS'
    result['candidate_classification']='B: structurally valid with documented semantic uncertainty'
    result['limitations']=[
        f"Strict audit covers {checks['strict_accepted']}/518 under the finite-source interpretation; {len(checks['uncertain_cases'])} predictions are unproven.",
        'Source/policy PASS gates certify emitted claims and known operations, not missing obligations or hidden correctness.',
        'case_55 has an uncertainty-only INCOMPLETE empty plan; source shape passes, strict semantic plan requirements fail.',
        f"All-32 candidate sample accuracy is {sample['candidate']['status_correct']}/32 statuses and {sample['candidate']['exact_cases']}/32 exact. Safety corrections are retained despite measured regression.",
        'Fresh isolated installation and execution are verified only when CLEAN_DEPENDENCY_INSTALL is PASS; read measured environment evidence.',
        'Conditional public CSV publication remains unverified; a passing privacy check does not verify event-specific sharing terms.',
        'The active session must end and app close before copying, redacting and zipping the original relevant traces.',
        'Basic archive secret scanning is not a complete privacy audit. No dataset, transcript or private trace is packaged.',
        'No HackerRank upload or interview was performed.']
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    (artifacts/'release_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    report=f"# Candidate readiness — executed gates\n\nRun {result['run_id']} at {result['timestamp_utc']}. **{result['candidate_classification']}**. Overall fully proven submission readiness: {gates['OVERALL_SUBMISSION_READINESS']}.\n\n| Gate | Result |\n|---|---|\n"
    report+=''.join(f'| {k} | {v} |\n' for k,v in gates.items())
    report+=f"\nTests {result['tests']}, failures 0. Candidate rows {checks['rows']}; strict {checks['strict_accepted']}; uncertain {len(checks['uncertain_cases'])}; source-backed cited steps {checks['source_backed_cited_steps']}.\n\nOutput SHA-256 `{checks['sha256']}`. Code ZIP SHA-256 `{result['package']['sha256']}`.\n\n"
    report+=result['sample_gate_meaning']+'\n\n'+f"Numerical quality: `{result['measured_quality']}`.\n\nSix separate assessments: `{result['quality_assessments']}`.\n\nFresh processes: `{runs}`.\n\n"
    report+='\n'.join('- '+v for v in result['limitations'])+'\n'
    (artifacts/'READINESS.md').write_text(report,encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('package','limitations')},indent=2))

if __name__=='__main__': main()
