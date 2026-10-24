"""GhostGuard: independently retrieve original sources and reject unsupported plans.

This deterministic reviewer cannot turn an unresolved state into a guessed answer.
It reports concrete challenges; one fresh primary investigation is the maximum retry.
"""
from pathlib import Path
import hashlib
import re
from .models import timestamp,tokens
from .loader import contained_path
from .adapters import EvidenceIndex,restricted_sql,COLLECTIONS,DEFAULT_CATEGORY
from .validator import validate_audit
from .relationships import RelationshipIndex


class ReviewError(ValueError):
    pass


def rejection_category(message):
    if 'changed during' in message: return 'SOURCE_INTEGRITY'
    if 'identity binding' in message or 'resource ownership' in message: return 'IDENTITY_CONFLICT'
    if 'no subject-linked profile' in message: return 'MISSING_PROFILE_LINK_OR_PROOF'
    if 'Missing linked resource' in message: return 'RETRIEVAL_OMISSION'
    if 'Missing bound resource' in message or 'no admissible' in message or 'Unresolved state' in message: return 'MISSING_EVIDENCE'
    if 'Unsupported source' in message: return 'UNSUPPORTED_SOURCE_OR_STATE'
    if 'Missing final verification' in message: return 'MISSING_VERIFICATION'
    if 'Unsafe deletion' in message: return 'POLICY_SAFETY'
    if 'Conflicting' in message: return 'CONTRADICTION'
    return 'CONTRACT_OR_POLICY'


class GhostGuard:
    def __init__(self,corpus,index):
        self.corpus,self.index=corpus,index
        self.source_rows={r['file_id']:r for r in corpus.manifest}
        self.activities={r['activity_id']:r for r in corpus.activities}
        self.raw_cache={}
        self.reparsed={}
        self.scan=[(f,f.binding_tokens) for f in index.facts]
        self.reviewed=0
        self.challenges=0
        self.challenged_cases=set()
        self.relationships=RelationshipIndex(corpus,index)

    def refresh(self,index):
        if any(self.index.source_hashes.get(k)!=v for k,v in index.source_hashes.items()):
            raise ReviewError('Source changed during targeted review')
        self.index=index
        self.relationships=RelationshipIndex(self.corpus,index)
        self.scan=[(f,f.binding_tokens) for f in index.facts]

    def source_supports(self,fact):
        """Fetch original source, not primary summary; check locator/scope membership."""
        if fact.source in self.activities:
            row=self.activities[fact.source]
            confirmed=(row['event_type']=='CHECK_DATA_FLOW' and 'remains enabled' in row['details']) or (
                row['event_type']=='CHECK_RESTORE_ACCESS' and 'can still be restored' in row['details'])
            return (confirmed and row['resource_id']==fact.resource and row['target_system']==fact.system
                    and fact.category==DEFAULT_CATEGORY.get(fact.system) and fact.state=='ACTIVE'
                    and fact.observed==timestamp(row['event_time']) and fact.captured==timestamp(row['event_time']))
        row=self.source_rows.get(fact.source)
        if not row: return False
        path=contained_path(self.corpus.root,row['file_path'])
        if hashlib.sha256(path.read_bytes()).hexdigest()!=self.index.source_hashes[fact.source]:
            return False
        if fact.source not in self.raw_cache:
            if path.suffix=='.sql':
                self.raw_cache[fact.source]=restricted_sql(path.read_text(encoding='utf-8'))
            elif path.suffix in ('.png','.pdf'):
                self.raw_cache[fact.source]=self.index.media[fact.source]
            else: self.raw_cache[fact.source]=path.read_text(encoding='utf-8')
        raw=self.raw_cache[fact.source]
        if path.suffix=='.sql':
            if fact.locator=='scoped inventory absence':
                table=raw.get(fact.scope)
                if table is None: return False
                scoped=[r for r in table if ('origin_system' not in r or
                    (r['origin_system']==fact.system and COLLECTIONS.get(r.get('collection_name'),('',''))[1]==fact.category))]
                return not any(r.get('resource_id')==fact.resource for r in scoped)
        if fact.source not in self.reparsed:
            fresh=EvidenceIndex.__new__(EvidenceIndex)
            fresh.facts=[]; fresh.snapshots=[]; fresh.media={}
            source={**row,'_captured':timestamp(row['captured_at'])}
            if path.suffix=='.sql': fresh.sql(source,raw)
            elif path.suffix=='.json':
                import json
                fresh.json(source,json.loads(raw))
            elif path.suffix=='.log': fresh.logs(source,raw)
            elif path.suffix=='.txt': fresh.text(source,raw)
            elif path.suffix in ('.pdf','.png'):
                fresh.media={fact.source:raw}
                fresh.link_documents(self.corpus)
            self.reparsed[fact.source]=fresh.facts
        return any((f.system,f.resource,f.category,f.state,f.observed,f.scope)==
                   (fact.system,fact.resource,fact.category,fact.state,fact.observed,fact.scope)
                   for f in self.reparsed[fact.source])

    def review(self,audit,policy,aliases):
        validate_audit(audit,self.corpus.sources)
        self.reviewed+=1
        if audit.status=='NOT_APPLICABLE': return []
        cutoff=timestamp(audit.case['audit_at'])
        issues=[]
        fact_map={(f.system,f.resource):f for f in audit.facts}
        if audit.bindings:
            for key,link in audit.bindings.items():
                if not self.relationships.validates(key,link,aliases,cutoff,audit.bindings):
                    issues.append(f'Invalid identity binding: {key[0]}/{key[1]}')
                if key not in fact_map:
                    issues.append(f'Missing bound resource state: {key[0]}/{key[1]}')
        if audit.status=='COMPLETE' and not any(
            (f.category=='USER_PROFILE' and f.state=='ABSENT') or
            (f.category=='ACCOUNT_TOMBSTONE' and f.state=='REDACTED') for f in audit.facts):
            issues.append('Unsupported COMPLETE: no subject-linked profile absence or compliant tombstone proof')
        for fact in audit.facts:
            if not fact.admissible(cutoff) or not self.source_supports(fact):
                issues.append(f'Unsupported source: {fact.system}/{fact.resource}/{fact.source}')
            if fact.data.get('_link_at') and timestamp(fact.data['_link_at'])>cutoff:
                issues.append(f'Future identity binding: {fact.resource}')
            if fact.state=='UNKNOWN': issues.append(f'Unproven state: {fact.resource}')
            ops={s['operation'] for s in audit.steps if (s['system_id'],s['resource_id'])==(fact.system,fact.resource)}
            violation=policy.violation(fact,cutoff)
            finding,remediation,verification=policy.operations(fact,cutoff)
            if violation and (finding not in ops or remediation not in ops):
                issues.append(f'Missing policy finding/remediation: {fact.resource}')
            if fact.state=='ABSENT' and verification in ('VERIFY_RECORD_REDACTED','VERIFY_RECORD_ANONYMIZED'):
                verification='VERIFY_RECORD_ABSENT'
            if verification not in ops: issues.append(f'Missing final verification: {fact.resource}')
            if fact.category in ('SECURITY_AUDIT_LOG','LEGAL_HOLD_RECORD','ACCOUNT_TOMBSTONE','BACKUP_ARCHIVE') and policy.action(fact,cutoff)!='DELETE' and 'DELETE_RECORD' in ops:
                issues.append(f'Unsafe deletion of retained resource: {fact.resource}')
        for step in audit.steps:
            key=step['system_id'],step['resource_id']
            fact=fact_map.get(key)
            if not fact: issues.append(f'Uninvestigated step resource: {key}')
            else:
                finding,remedy,verification=policy.operations(fact,cutoff)
                if fact.state=='ABSENT' and verification in ('VERIFY_RECORD_REDACTED','VERIFY_RECORD_ANONYMIZED'):
                    verification='VERIFY_RECORD_ABSENT'
                permitted={('VERIFICATION',verification)}
                if policy.violation(fact,cutoff):
                    permitted.update({('FINDING',finding),('REMEDIATION',remedy)})
                if (step['phase'],step['operation']) not in permitted:
                    issues.append(f'Unsupported policy operation/state: {key}/{step["operation"]}')
                if step['evidence_id'] and step['evidence_id']!=fact.source:
                    issues.append(f'Citation is not the supporting source: {key}')
        # Fresh scan for missing source-linked resources, independent of primary retrieval index.
        for fact,source_tokens in self.scan:
            if not fact.admissible(cutoff): continue
            if fact.data.get('_link_at') and timestamp(fact.data['_link_at'])>cutoff: continue
            if aliases & source_tokens:
                if (fact.system,fact.resource) not in fact_map:
                    issues.append(f'Missing linked resource: {fact.system}/{fact.resource}')
        self.challenges+=len(set(issues))
        if issues: self.challenged_cases.add(audit.case['case_id'])
        return sorted(set(issues))
