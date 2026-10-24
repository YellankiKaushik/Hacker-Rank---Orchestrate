from collections import defaultdict
from dataclasses import replace
from .models import Audit, Fact, timestamp, tokens
from .identity import IdentityGraph
from .intent import deletion_intent
from .policy import Policy
from .compiler import compile_steps


class UnresolvedCase(ValueError):
    pass


class Engine:
    def __init__(self,corpus,index):
        self.corpus,self.index = corpus,index
        self.identity = IdentityGraph(corpus.identities,corpus.history)
        self.policy = Policy(corpus.rules)

    def investigate(self,case):
        if not deletion_intent(case['request_text']):
            return Audit(case,'',[],'NOT_APPLICABLE',[])
        cutoff = timestamp(case['audit_at'])
        subject,aliases = self.identity.resolve(case['email'],cutoff)
        keys = set()
        matched_sources = set()
        for alias in aliases:
            for f in self.index.by_token.get(alias,[]):
                if f.admissible(cutoff) and (not f.data.get('_link_at') or timestamp(f.data['_link_at'])<=cutoff):
                    keys.add((f.system,f.resource)); matched_sources.add(f.source)
        # Temporal resource bindings are established by real observations/catalog entries.
        for row in self.corpus.activities:
            if row['event_type']=='LINK_RESOURCE_IDENTITY' and timestamp(row['event_time'])<=cutoff and aliases & tokens(row['details']):
                keys.add((row['target_system'],row['resource_id']))
        selected = []
        issues = []
        for key in sorted(keys):
            observations = [f for f in self.index.by_resource[key] if f.admissible(cutoff)]
            if not observations: continue
            categories = {f.category for f in observations}
            # Use positive source-scoped inventory queries to prove missing rows, never lack of retrieved files.
            for snapshot in self.index.snapshots:
                if (snapshot.source in matched_sources and snapshot.system==key[0]
                    and snapshot.category in categories and snapshot.captured<=cutoff
                    and key[1] not in snapshot.resources):
                    observations.append(Fact(snapshot.source,snapshot.captured,snapshot.observed,key[0],key[1],
                        snapshot.category,'ABSENT',{'_query_resource':key[1]},snapshot.scope,'scoped inventory absence'))
            latest_time = max(f.observed for f in observations)
            latest = [f for f in observations if f.observed==latest_time]
            # At one instant, every replica must comply; positive violating copies beat a primary absence.
            latest.sort(key=lambda f:(bool(self.policy.violation(f,cutoff)),f.captured,f.source,f.scope),reverse=True)
            fact = latest[0]
            if len({f.state for f in latest})>1:
                issues.append(f'Conflicting simultaneous observations: {key[0]}/{key[1]}')
            if fact.state=='UNKNOWN':
                # A mere archive listing proves storage, not whether restore access is open.
                issues.append(f'Unresolved state: {key[0]}/{key[1]}')
                continue
            selected.append(fact)
        if any(issue.startswith('Unresolved state:') for issue in issues):
            raise UnresolvedCase(f'{case["case_id"]}: '+ '; '.join(issues))
        if not selected:
            raise UnresolvedCase(f'{case["case_id"]}: no admissible subject-linked state evidence')
        status,steps = compile_steps(selected,self.policy,cutoff)
        return Audit(case,subject,selected,status,steps,issues)
