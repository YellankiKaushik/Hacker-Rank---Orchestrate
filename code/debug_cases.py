"""Local source diagnostics. Never imported by the prediction engine."""
from pathlib import Path
import sys
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.engine import Engine
from ghosttrace.models import timestamp,tokens

root=Path(__file__).resolve().parents[1]
c=Corpus(root/'dataset'); idx=EvidenceIndex(c,root/'tmp/ocr'); e=Engine(c,idx)
cases=read_csv(root/'dataset/deletion_requests.csv')+read_csv(root/'dataset/sample_deletion_requests.csv')
for case in cases:
    if case['case_id'] not in sys.argv[1:]: continue
    uid,aliases=e.identity.resolve(case['email'],timestamp(case['audit_at']))
    print('\nCASE',case['case_id'],'SUBJECT',uid,'cutoff',case['audit_at'])
    facts=[f for f in idx.facts if tokens(f.data)&aliases]
    print('linked facts',len(facts))
    for f in facts[:30]: print(f.source,f.system,f.resource,f.category,f.state,f.observed.isoformat(),f.captured.isoformat())
    for row in c.manifest:
        path=c.root/row['file_path']
        if path.suffix not in ('.png','.pdf'):
            text=path.read_text(encoding='utf-8')
            if any(a in text.casefold() for a in aliases):
                print('raw source hit',row['file_id'],path.name)
