"""Read-only relationship/proof census over participant sources, never references."""
from collections import Counter,defaultdict
import json
from pathlib import Path
import re
import sys
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.adapters import EvidenceIndex,restricted_sql
from ghosttrace.engine import Engine
from ghosttrace.models import timestamp,tokens

ROOT=Path(__file__).resolve().parents[1]


def audit():
    corpus=Corpus(ROOT/'dataset'); index=EvidenceIndex(corpus,ROOT/'tmp/ocr')
    engine=Engine(corpus,index)
    cases=read_csv(ROOT/'dataset/deletion_requests.csv')+read_csv(ROOT/'dataset/sample_deletion_requests.csv')
    relations=[]
    def walk(node,where):
        if isinstance(node,dict):
            if 'resource_id' in node:
                refs={k:v for k,v in node.items() if k!='resource_id' and isinstance(v,str)
                      and any(r!=node['resource_id'] for r in re.findall(r'\b(?:account|tombstone|search|analytics|support|export|backup|data_flow)_\d+\b',v))}
                if refs: relations.append((where,node['resource_id'],refs))
            for key,v in node.items(): walk(v,where)
        elif isinstance(node,list):
            for v in node: walk(v,where)
    for source in corpus.manifest:
        path=corpus.root/source['file_path']
        if path.suffix=='.json': walk(json.loads(path.read_text()),source['file_id'])
        elif path.suffix=='.sql':
            for table,rows in restricted_sql(path.read_text()).items():
                for row in rows:
                    if 'record_json' in row: walk(json.loads(row['record_json']),source['file_id']+'/'+table)
                    else: walk(row,source['file_id']+'/'+table)
    activity_identifiers=Counter(row['event_type'] for row in corpus.activities if tokens(row['details']) & set(engine.identity.identities))
    chosen=[]
    for case in cases:
        if sys.argv[1:] and case['case_id'] not in sys.argv[1:]: continue
        if not sys.argv[1:] and case['case_id'] not in ('case_103','case_150','case_213','case_55'): continue
        cutoff=timestamp(case['audit_at']); uid,aliases=engine.identity.resolve(case['email'],cutoff)
        admissible=[f for f in index.facts if f.admissible(cutoff) and aliases & tokens(f.data.get('_bindings',f.data))]
        excluded=[f for f in index.facts if not f.admissible(cutoff) and aliases & tokens(f.data.get('_bindings',f.data))]
        chosen.append({'case_id':case['case_id'],'subject':uid,'cutoff':case['audit_at'],
            'admissible':[(f.source,f.system,f.resource,f.category,f.state) for f in admissible],
            'excluded_future':[(f.source,f.resource,f.state) for f in excluded],
            'eligible_files':sum(timestamp(r['captured_at'])<=cutoff for r in corpus.manifest)})
    summary={'facts':len(index.facts),'activity_explicit_subject_link_types':dict(activity_identifiers),
        'structured_cross_resource_relations':relations,'cases':chosen}
    (ROOT/'tmp/recovery_audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({**summary,'structured_cross_resource_relations':relations[:12]},indent=2))


if __name__=='__main__': audit()
