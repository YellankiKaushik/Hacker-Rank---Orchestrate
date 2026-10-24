"""Build a development source ZIP and verify its clean extraction without uploading."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    output=ROOT/'code.zip'
    code=ROOT/'code'
    members=[ROOT/'README.md']+[p for p in code.rglob('*') if p.is_file()
        and p.suffix in ('.py','.md','.txt','.ps1')
        and not any(part in ('__pycache__','.venv','venv','node_modules') for part in p.parts)]
    required={'README.md','code/main.py','code/requirements.txt','code/ghosttrace/ocr.ps1',
              'code/evaluation/evaluation_report.md','code/evaluation/usage_report.md','code/docs/UNRESOLVED_ISSUES.md'}
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(members): archive.write(path,path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as archive:
        names=set(archive.namelist())
        if not required<=names: raise ValueError('Package missing required source/report files')
        for name in names:
            parts=PurePosixPath(name).parts
            if '..' in parts or name.startswith('/') or parts[0] not in ('code','README.md'):
                raise ValueError('Unsafe archive path')
            if any(p in ('dataset','__pycache__','.git','agent-trace','node_modules','.venv','venv') for p in parts):
                raise ValueError('Forbidden package member')
            if Path(name).suffix in ('.zip','.tar','.gz','.tgz','.7z','.rar','.jsonl','.db'):
                raise ValueError('Nested archive or private trace in package')
        if archive.testzip(): raise ValueError('ZIP integrity failure')
    temp_root=ROOT/'tmp'; temp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='package-check-',dir=temp_root) as directory:
        directory=Path(directory)
        with zipfile.ZipFile(output) as archive: archive.extractall(directory)
        tests=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','code/tests','-q'],cwd=directory,capture_output=True,text=True)
        if tests.returncode: raise RuntimeError('Extracted test suite failed: '+tests.stderr[-2000:])
        # Source-only extraction uses the unchanged external dataset and a warm source-hashed OCR cache.
        sample_script=(
            "import sys,json;from pathlib import Path;sys.path.insert(0,'code');"
            "from main import run;from evaluation.main import compare;from ghosttrace.loader import read_csv;"
            f"d=Path({str(ROOT/'dataset')!r});cache=Path({str(ROOT/'tmp/ocr')!r});"
            "a,m,c,i=run(d,d/'sample_deletion_requests.csv',Path('sample.csv'),cache,True,True);"
            "s=compare(a,read_csv(d/'sample_output.csv'));"
            "print(json.dumps({'status_correct':s['status_correct'],'exact_cases':s['exact_cases'],'unresolved':len(m['unresolved'])}))")
        sample=subprocess.run([sys.executable,'-X','utf8','-c',sample_script],cwd=directory,capture_output=True,text=True)
        if sample.returncode: raise RuntimeError('Extracted sample execution failed: '+sample.stderr[-2000:])
        observed=json.loads(sample.stdout)
        current=json.loads((ROOT/'tmp/checkpoint.json').read_text())
        if observed['status_correct']!=current['sample_status'] or observed['exact_cases']!=current['sample_exact']:
            raise ValueError('Extracted source differs from checkpoint metrics')
        full=subprocess.run([sys.executable,'-X','utf8','code/main.py','--dataset',str(ROOT/'dataset'),
            '--cache-dir',str(ROOT/'tmp/ocr'),'--output',str(directory/'output.csv')],cwd=directory,capture_output=True,text=True)
        # Failing closed for current blockers is expected, not a successful submission run.
        unresolved=current['full_unresolved']
        expected_block=(full.returncode!=0 and not (directory/'output.csv').exists()
                        and f'{unresolved} unresolved cases' in full.stderr) if unresolved else False
        if unresolved and not expected_block:
            raise ValueError('Unexpected clean full-run behavior; inspect release gate')
        if not unresolved and (full.returncode!=0 or not (directory/'output.csv').exists()):
            raise ValueError('Clean full-run prediction gate failed')
        result={'package':'code.zip','bytes':output.stat().st_size,
            'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'members':len(names),
            'extracted_tests_passed':True,'extracted_sample':observed,
            'extracted_full_run_expected_block':expected_block,'submission_ready':not bool(unresolved),
            'validation_context':'source-only extraction, installed Python/pypdf, external unchanged dataset, warm OCR cache'}
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    (artifacts/'package_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
