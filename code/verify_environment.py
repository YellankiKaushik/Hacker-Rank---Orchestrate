"""Verify dependency isolation inside an already freshly installed virtualenv."""
import hashlib
import json
from pathlib import Path
import site
import sys
import pypdf

ROOT=Path(__file__).resolve().parents[1]

def verify():
    prefix=Path(sys.prefix).resolve(); package=Path(pypdf.__file__).resolve()
    config=prefix/'pyvenv.cfg'
    isolated=(sys.prefix!=sys.base_prefix and package.is_relative_to(prefix)
              and site.ENABLE_USER_SITE is False and config.exists()
              and 'include-system-site-packages = false' in config.read_text())
    result={'gate':'PASS' if isolated else 'FAIL','python':sys.version.split()[0],'pypdf':pypdf.__version__,
            'isolated_prefix':str(prefix),'package_inside_venv':package.is_relative_to(prefix),
            'user_site_enabled':site.ENABLE_USER_SITE,
            'requirements_sha256':hashlib.sha256((ROOT/'code/requirements.txt').read_bytes()).hexdigest(),
            'installation_context':'Fresh venv; ensurepip bootstrap; pinned dependency installed from https://pypi.org/simple; workspace TEMP workaround for sandbox ACL.'}
    target=ROOT/'artifacts/clean_env_verification.json'; target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    if not isolated: raise ValueError('Dependency isolation verification failed')
    print(json.dumps({k:v for k,v in result.items() if k!='isolated_prefix'},indent=2))
    return result

if __name__=='__main__': verify()
