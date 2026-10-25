from collections import defaultdict
from dataclasses import replace
from .models import Audit, Fact, timestamp, tokens
from .identity import IdentityGraph
from .policy import Policy
from .compiler import compile_steps
from .relationships import RelationshipIndex,declared_subjects
from .adapters import DEFAULT_CATEGORY
from .adapters import EvidenceIndex
from .intent_resolution import resolve
from types import SimpleNamespace
import hashlib


class UnresolvedCase(ValueError):
    pass


class Engine:
    def __init__(self,corpus,index,intent_ai=None):
        self.corpus,self.index = corpus,index
        self.identity = IdentityGraph(corpus.identities,corpus.history)
        self.policy = Policy(corpus.rules)
        self.relationships=RelationshipIndex(corpus,index)
        self.intent_ai=intent_ai
        self._reinvestigation_cache={}
        self.source_cache_hits=0
        self.source_reads=0

    def investigate(self,case,permit_partial=False):
        resolution=resolve(case['request_text'],self.intent_ai)
        intent=resolution.decision
        if not intent:
            return Audit(case,'',[],'NOT_APPLICABLE',[],intent_resolution=resolution)
        cutoff = timestamp(case['audit_at'])
        subject,aliases = self.identity.resolve(case['email'],cutoff)
        bindings=self.relationships.bind(subject,aliases,cutoff)
        keys = set(bindings)
        selected = []
        issues = []
        for key in sorted(keys):
            observations = [f for f in self.index.by_resource[key] if f.admissible(cutoff)]
            categories = {f.category for f in observations}
            if not categories and key[0] in DEFAULT_CATEGORY:
                categories.add(DEFAULT_CATEGORY[key[0]])
            # Use positive source-scoped inventory queries to prove missing rows, never lack of retrieved files.
            for snapshot in self.index.snapshots:
                if (snapshot.exhaustive is True and snapshot.system==key[0]
                    and snapshot.category in categories and snapshot.captured<=cutoff and snapshot.observed<=cutoff
                    and key[1] not in snapshot.resources):
                    observations.append(Fact(snapshot.source,snapshot.captured,snapshot.observed,key[0],key[1],
                        snapshot.category,'ABSENT',{'_query_resource':key[1],'_query_system':key[0]},snapshot.scope,'scoped inventory absence'))
            if not observations:
                issues.append(f'Linked resource has no admissible state: {key[0]}/{key[1]}')
                continue
            if categories & {'BACKUP_ARCHIVE','DATA_FLOW'}:
                known=[f for f in observations if f.state!='UNKNOWN']
                # A later storage listing observes existence, not a permission/configuration change.
                if known: observations=[f for f in observations if f.state!='UNKNOWN' or f.data.get('_control_observation')
                                        or any(k in f.data for k in ('enabled','restore_allowed','eligible','decision','restore_blocked','disabled'))]
            latest_time = max(f.observed for f in observations)
            latest = [f for f in observations if f.observed==latest_time]
            # At one instant, every replica must comply; positive violating copies beat a primary absence.
            latest.sort(key=lambda f:(bool(self.policy.violation(f,cutoff)),f.captured,f.source,f.scope),reverse=True)
            fact = latest[0]
            if categories & {'BACKUP_ARCHIVE','DATA_FLOW'} and len({f.state for f in latest})>1:
                issues.append(f'Unresolved state: {key[0]}/{key[1]} (conflicting simultaneous controls)')
                continue
            replica_latest={}
            for observed in observations:
                if observed.copy_role!='REPLICA': continue
                prior=replica_latest.get(observed.scope)
                if prior is None or observed.observed>prior.observed:
                    replica_latest[observed.scope]=observed
                elif observed.observed==prior.observed and self.policy.violation(observed,cutoff):
                    replica_latest[observed.scope]=observed
            remaining=[f for f in replica_latest.values() if self.policy.violation(f,cutoff)]
            if remaining and not self.policy.violation(fact,cutoff):
                issues.append(f'Conflicting replica scope: {key[0]}/{key[1]}')
                fact=max(remaining,key=lambda f:(f.observed,f.captured,f.source))
            owners=declared_subjects(fact,set(self.identity.identities))
            if owners and owners!={subject}:
                raise UnresolvedCase(f'{case["case_id"]}: conflicting resource ownership at {fact.source}/{fact.resource}')
            if len({f.state for f in latest})>1:
                issues.append(f'Conflicting simultaneous observations: {key[0]}/{key[1]}')
            if (fact.category=='SUPPORT_ATTACHMENT' and self.policy.action(fact,cutoff)=='DELETE'
                    and 'shared_subjects' in fact.data and subject not in fact.data['shared_subjects']):
                issues.append(f'Unresolved state: {key[0]}/{key[1]} (sole owner is not deletion subject)')
                continue
            if fact.state=='UNKNOWN' or self.policy.action(fact,cutoff)=='UNKNOWN':
                # A mere archive listing proves storage, not whether restore access is open.
                issues.append(f'Unresolved state: {key[0]}/{key[1]}')
                continue
            selected.append(fact)
        if not permit_partial and any(issue.startswith('Unresolved state:') for issue in issues):
            raise UnresolvedCase(f'{case["case_id"]}: '+ '; '.join(issues))
        if not selected and not permit_partial:
            raise UnresolvedCase(f'{case["case_id"]}: no admissible subject-linked state evidence')
        if not selected:
            issues.append('No admissible subject-linked state evidence; no current-state claim can be emitted')
        status,steps = compile_steps(selected,self.policy,cutoff)
        if permit_partial and (not selected or any(v.startswith(('Unresolved state:','Linked resource has no admissible state:')) for v in issues)):
            status='INCOMPLETE'
            for step in steps:
                if step['phase']!='FINDING': step['evidence_id']=''
        return Audit(case,subject,selected,status,steps,issues,bindings=bindings,intent_resolution=resolution)

    def reinvestigate(self,case,audit,max_sources=4):
        """Reread only admissible sources touching this subject; never invent a link.

        New facts can repair an indexing/cache omission. Unidentified 404s remain
        unidentified. A mutated source is rejected instead of silently trusted.
        """
        cutoff=timestamp(case['audit_at'])
        _,aliases=self.identity.resolve(case['email'],cutoff)
        candidates={f.source for f in self.index.facts if f.admissible(cutoff)
                    and aliases & f.binding_tokens}
        candidates.update(f.source for f in audit.facts)
        candidates.update(link.source for link in audit.bindings.values())
        rows=[r for r in self.corpus.manifest if r['file_id'] in candidates and timestamp(r['captured_at'])<=cutoff]
        rows=sorted(rows,key=lambda r:(r['captured_at'],r['file_id']),reverse=True)[:max_sources]
        for row in rows:
            path=self.corpus.root/row['file_path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=self.index.source_hashes[row['file_id']]:
                raise UnresolvedCase('Source changed during investigation; retry requires a new frozen run')
        if not rows: return audit,self.index,[]
        selected_ids={r['file_id'] for r in rows}
        cache_key=tuple(sorted(selected_ids))
        if cache_key in self._reinvestigation_cache:
            self.source_cache_hits+=1
            merged=self._reinvestigation_cache[cache_key]
            return Engine(self.corpus,merged,self.intent_ai).investigate(case),merged,sorted(selected_ids)
        self.source_reads+=len(rows)
        partial=EvidenceIndex(SimpleNamespace(root=self.corpus.root,manifest=rows,activities=self.corpus.activities),
                              getattr(self.index,'cache_dir',None))
        merged=EvidenceIndex.__new__(EvidenceIndex)
        combined=[f for f in self.index.facts if f.source not in selected_ids]+partial.facts
        dedup={(f.source,f.system,f.resource,f.observed,f.scope,f.locator):f for f in combined}
        merged.facts=list(dedup.values())
        merged.snapshots=[s for s in self.index.snapshots if s.source not in selected_ids]+partial.snapshots
        merged.media={**getattr(self.index,'media',{}),**partial.media}
        merged.coverage=getattr(self.index,'coverage',{})
        merged.cache_dir=getattr(self.index,'cache_dir',None)
        merged.source_hashes={**self.index.source_hashes,**partial.source_hashes}
        merged.rebuild_indexes()
        self._reinvestigation_cache[cache_key]=merged
        retried=Engine(self.corpus,merged,self.intent_ai).investigate(case)
        return retried,merged,sorted(selected_ids)
