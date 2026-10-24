"""Evidence-gap diagnostics. Does not turn orphan readbacks into predictions."""
from .models import timestamp,tokens
from .identity import IdentityGraph
from .relationships import RelationshipIndex,fact_tokens,declared_subjects


def binding_gap(case,corpus,index,context=None):
    cutoff=timestamp(case['audit_at'])
    graph=context.graph if context else IdentityGraph(corpus.identities,corpus.history)
    subject,aliases=graph.resolve(case['email'],cutoff)
    relations=context.relations if context else RelationshipIndex(corpus,index)
    links=relations.bind(subject,aliases,cutoff)
    scan=context.scan if context else [(f,fact_tokens(f)) for f in index.facts]
    linked=[f for f,keys in scan if f.admissible(cutoff) and aliases & keys]
    sources={f.source for f in linked}
    roots=[f for f in index.facts if f.admissible(cutoff) and f.source in sources
           and f.category in ('USER_PROFILE','ACCOUNT_TOMBSTONE')]
    known_subjects=set(graph.identities)
    excluded_other=[f for f in roots if declared_subjects(f,known_subjects) and subject not in declared_subjects(f,known_subjects)]
    roots=[f for f in roots if f not in excluded_other]
    bound=[f for f in roots if (f.system,f.resource) in links]
    orphan=[f for f in roots if (f.system,f.resource) not in links]
    # A count is evidence of ambiguity, not a rule for assigning rows by elimination.
    orphan_ids=sorted({(f.source,f.system,f.resource,f.state) for f in orphan})
    future_roots=[f for f,keys in scan if not f.admissible(cutoff)
                  and f.category in ('USER_PROFILE','ACCOUNT_TOMBSTONE') and aliases & keys]
    eligible={r['file_id'] for r in corpus.manifest if timestamp(r['captured_at'])<=cutoff}
    reason='EXPLICIT_LINKED_ROOT_STATE' if bound else 'MISSING_SUBJECT_TO_RESOURCE_LINK'
    if not roots and not bound: reason='NO_ROOT_STATE_IN_LINKED_ADMISSIBLE_SOURCES'
    if future_roots and not bound: reason='ROOT_BINDING_ONLY_IN_EXCLUDED_FUTURE_CAPTURE'
    return {'case_id':case['case_id'],'subject':subject,'cutoff':case['audit_at'],
        'eligible_source_count':len(eligible),'linked_sources':sorted(sources),
        'root_candidate_count':len({(f.system,f.resource) for f in roots}),
        'other_subject_root_records_ruled_out':len({(f.source,f.system,f.resource) for f in excluded_other}),
        'orphan_root_candidates':orphan_ids,'bound_root_count':len(bound),
        'future_root_sources':sorted({f.source for f in future_roots}),
        'reason':reason,'note':'No identities assigned by batch position, timing proximity, filename or numeric suffix'}


class GapAuditor:
    def __init__(self,corpus,index):
        self.corpus,self.index=corpus,index
        self.graph=IdentityGraph(corpus.identities,corpus.history)
        self.relations=RelationshipIndex(corpus,index)
        self.scan=[(f,fact_tokens(f)) for f in index.facts]

    def inspect(self,case):
        return binding_gap(case,self.corpus,self.index,self)
