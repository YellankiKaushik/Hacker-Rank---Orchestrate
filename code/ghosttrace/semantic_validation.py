"""Fresh-process semantic validation backed by source reparse and binding review.

Shares domain parsing/policy code; it is not an independent hidden-answer oracle.
"""
import json
from .loader import read_csv
from .models import Audit,timestamp
from .adapters import EvidenceIndex
from .engine import Engine
from .reviewer import GhostGuard
from .validator import validate_file


def validate_semantic_file(path,cases,corpus,cache_dir):
    count=validate_file(path,cases,corpus.sources)
    index=EvidenceIndex(corpus,cache_dir)
    engine=Engine(corpus,index)
    guard=GhostGuard(corpus,index)
    rows={r['case_id']:r for r in read_csv(path)}
    for case in cases:
        expected=engine.investigate(case)
        row=rows[case['case_id']]
        submitted=Audit(case,expected.subject,expected.facts,row['deletion_status'],json.loads(row['steps_json']),
                        expected.issues,expected.bindings)
        if submitted.status!=expected.status:
            raise ValueError(f'{case["case_id"]}: submitted status conflicts with source-derived state')
        aliases=engine.identity.aliases(timestamp(case['audit_at'])).get(expected.subject,set())
        challenges=guard.review(submitted,engine.policy,aliases)
        if challenges: raise ValueError(f'{case["case_id"]}: source review rejected artifact: '+ '; '.join(challenges))
    return count
