"""Build source ZIP and execute strict and candidate modes after clean extraction."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def build_archive(output,members,root):
    """Stable byte order, metadata and text newlines across clean Git checkouts."""
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(members,key=lambda p:p.relative_to(root).as_posix()):
            name=path.relative_to(root).as_posix()
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.create_system=3; info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,path.read_bytes().replace(b'\r\n',b'\n'),compresslevel=9)


def main():
    (ROOT/'tmp').mkdir(exist_ok=True)
    output=ROOT/'code.zip'
    code=ROOT/'code'
    members=[ROOT/'README.md']+[p for p in code.rglob('*') if p.is_file()
        and p.suffix in ('.py','.md','.txt','.ps1')
        and p.name!='FINAL_RELEASE_RECORD.md'
        and not any(part in ('__pycache__','.venv','venv','node_modules') for part in p.parts)]
    required={'README.md','code/main.py','code/requirements.txt','code/ghosttrace/ocr.ps1',
              'code/evaluation/evaluation_report.md','code/evaluation/usage_report.md','code/docs/UNRESOLVED_ISSUES.md'}
    build_archive(output,members,ROOT)
    first_hash=hashlib.sha256(output.read_bytes()).hexdigest()
    # Hash-bearing release record is excluded to avoid recursive archive hashes.
    with tempfile.TemporaryDirectory(prefix='zip-rebuild-',dir=ROOT/'tmp') as rebuild:
        second=Path(rebuild)/'code.zip'; build_archive(second,members,ROOT)
        if hashlib.sha256(second.read_bytes()).hexdigest()!=first_hash:
            raise ValueError('Source archive bytes are not reproducible')
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
        if not directory.resolve().is_relative_to(temp_root.resolve()):
            raise ValueError('Package extraction escaped the intended temporary workspace')
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
        candidate=subprocess.run([sys.executable,'-X','utf8','code/main.py','--mode','candidate','--dataset',str(ROOT/'dataset'),
            '--cache-dir',str(ROOT/'tmp/ocr'),'--output',str(directory/'output.csv')],cwd=directory,capture_output=True,text=True,timeout=60)
        if candidate.returncode: raise ValueError('Clean candidate generation failed: '+candidate.stderr[-1000:])
        candidate_hash=hashlib.sha256((directory/'output.csv').read_bytes()).hexdigest()
        if candidate_hash!=current['output_sha256']: raise ValueError('Clean candidate differs from measured output')
        check=subprocess.run([sys.executable,'-X','utf8','code/validate_candidate.py','--dataset',str(ROOT/'dataset'),
            '--cache-dir',str(ROOT/'tmp/ocr'),'--output',str(directory/'output.csv'),
            '--report',str(directory/'candidate_validation.json')],cwd=directory,capture_output=True,text=True,timeout=60)
        if check.returncode: raise ValueError('Extracted candidate source checks failed: '+check.stderr[-1000:])
        verified=json.loads((directory/'candidate_validation.json').read_text())
        result={'package':'code.zip','bytes':output.stat().st_size,
            'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'members':len(names),
            'extracted_tests_passed':True,'extracted_sample':observed,
            'extracted_full_run_expected_block':expected_block,'submission_ready':not bool(unresolved),
            'candidate_rows':verified['rows'],'candidate_sha256':candidate_hash,'candidate_source_checks':'PASS',
            'candidate_semantic_certainty':verified['SEMANTIC_CERTAINTY'],
            'deterministic_archive_rebuild':'PASS',
            'archive_metadata':'Sorted members, fixed 1980 ZIP epoch, normalized LF text, fixed regular-file permissions; FINAL_RELEASE_RECORD.md excluded to avoid self-referential hash.',
            'validation_context':'source-only extraction, installed Python/pypdf, external unchanged dataset, warm OCR cache'}
    artifacts=ROOT/'artifacts'; artifacts.mkdir(exist_ok=True)
    (artifacts/'package_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
