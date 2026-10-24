"""Inspect candidate contents without equating privacy PASS with contest permission."""
import hashlib
import json
import os
from pathlib import Path
import re
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.validator import validate_file
from ghosttrace.candidate import validate_candidate_file

ROOT=Path(__file__).resolve().parents[1]

def inspect_output(path,corpus,cases):
    validate_candidate_file(path,cases,corpus.sources)
    body=Path(path).read_bytes(); text=body.decode('utf-8-sig'); failures=[]
    patterns={'email':r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
              'private_path':r'[A-Za-z]:[\\/]|/Users/|/home/',
              'secret_prefix':r'sk-[A-Za-z0-9_-]{25,}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN .*PRIVATE KEY-----'}
    for category,pattern in patterns.items():
        if re.search(pattern,text): failures.append(category)
    configured=[v.encode() for k,v in os.environ.items() if re.search(r'(?:API_KEY|ACCESS_TOKEN|SECRET_KEY)$',k) and len(v)>=12]
    if any(v in body for v in configured): failures.append('configured_secret_value')
    steps=0
    for row in read_csv(path):
        if not re.fullmatch(r'case_\d+',row['case_id']): failures.append('noncanonical_case_identifier')
        for step in json.loads(row['steps_json']):
            steps+=1
            for field in ('system_id','resource_id'):
                if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*',step[field]): failures.append('non_identifier_scope')
    return {'privacy_gate':'FAIL' if failures else 'PASS','findings_categories_only':sorted(set(failures)),
            'rows':len(cases),'steps':steps,'sha256':hashlib.sha256(body).hexdigest(),
            'content':'Only prescribed case/status/step fields, stable IDs, enum values and numbering; no raw identities or evidence text.',
            'contest_publication_permission':'NOT VERIFIED',
            'publication_decision':'Withhold public output commit until contest-specific publication terms are verified; record hash in tracked release record.',
            'rules_checked':['Official local AGENTS.md, problem_statement.md, README.md',
                             'https://www.hackerrank.com/hackerrank-orchestrate-october26',
                             'https://www.hackerrank.com/about-us/terms-of-service'],
            'limitation':'Public instructions and general content ownership do not verify contest-specific embargo/sharing terms. Registration redirected to login; Windows browser automation stopped because URL could not be verified.'}

def main():
    corpus=Corpus(ROOT/'dataset')
    result=inspect_output(ROOT/'output.csv',corpus,read_csv(ROOT/'dataset/deletion_requests.csv'))
    path=ROOT/'artifacts/output_publication_check.json'; path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if result['privacy_gate']!='PASS': raise ValueError('Output content review failed')

if __name__=='__main__': main()
