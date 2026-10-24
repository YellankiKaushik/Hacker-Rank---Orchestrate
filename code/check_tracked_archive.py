"""Rebuild code.zip from committed Git blobs, ignoring private/untracked content."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from package_submission import build_archive

ROOT=Path(__file__).resolve().parents[1]

def main():
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    names=subprocess.check_output(['git','ls-tree','-r','-z','--name-only',commit,'--','README.md','code'],cwd=ROOT).decode().split('\0')
    (ROOT/'tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tracked-archive-',dir=ROOT/'tmp') as temp:
        root=Path(temp).resolve()
        if not root.is_relative_to((ROOT/'tmp').resolve()): raise ValueError('Snapshot escaped workspace')
        members=[]
        for name in names:
            if not name or Path(name).suffix not in ('.py','.md','.txt','.ps1') or Path(name).name=='FINAL_RELEASE_RECORD.md': continue
            path=(root/name).resolve()
            if not path.is_relative_to(root): raise ValueError('Unsafe committed path')
            body=subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=ROOT)
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(body); members.append(path)
        rebuilt=root/'code.zip'; build_archive(rebuilt,members,root)
        observed=hashlib.sha256(rebuilt.read_bytes()).hexdigest()
    expected=hashlib.sha256((ROOT/'code.zip').read_bytes()).hexdigest()
    result={'gate':'PASS' if observed==expected else 'FAIL','commit':commit,'archive_sha256':expected,
            'rebuilt_from_git_sha256':observed,'members':len(members),
            'context':'Tracked Git blobs only; fixed ZIP metadata and normalized LF; hash-bearing release record excluded.'}
    (ROOT/'artifacts/tracked_archive_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if observed!=expected: raise ValueError('ZIP differs from committed source')

if __name__=='__main__': main()
