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
from .intent import deletion_intent,AmbiguousIntent
from .intent_resolution import validated_decision
from .invariants import authorization_veto,original_records,raw_state_veto,raw_operation_veto


class ReviewError(ValueError):
    pass


def rejection_category(message):
    if 'changed during' in message: return 'SOURCE_INTEGRITY'
    if 'identity binding' in message or 'resource ownership' in message: return 'IDENTITY_CONFLICT'
    if 'no subject-linked profile' in message or 'required deletion coverage' in message: return 'MISSING_PROFILE_LINK_OR_PROOF'
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
        self.original_rows={}
        # Rebuild obligations from original files, not the primary's facts/token index.
        # Shared extraction/policy remain a documented independence limitation.
        self.obligation_index=EvidenceIndex(corpus,getattr(index,'cache_dir',None)) if corpus.manifest and hasattr(corpus,'root') else index
        self.scan=[(f,f.binding_tokens) for f in self.obligation_index.facts]
        self.reviewed=0
        self.challenges=0
        self.challenged_cases=set()
        self.relationships=RelationshipIndex(corpus,self.obligation_index)

    def refresh(self,index):
        if any(self.index.source_hashes.get(k)!=v for k,v in index.source_hashes.items()):
            raise ReviewError('Source changed during targeted review')
        self.index=index
        self.relationships=RelationshipIndex(self.corpus,self.obligation_index)

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
        if fact.captured!=timestamp(row['captured_at']): return False
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
        records=original_records(raw,path.suffix,fact.scope,fact.locator,fact.resource,fact.observed)
        self.original_rows[(fact.source,fact.scope,fact.locator,fact.resource,fact.observed)]=records
        if raw_state_veto(fact,records): return False
        if path.suffix=='.sql':
            if fact.locator=='scoped inventory absence':
                # Independently check physical relation semantics, source time and keyed selector.
                physical={'customer_profiles_primary':('account_service','USER_PROFILE'),
                          'customer_profiles_failover_replica':('account_service','USER_PROFILE'),
                          'search_documents_primary':('search_service','SEARCH_INDEX_ENTRY')}
                if physical.get(fact.scope)!=(fact.system,fact.category): return False
                source_text=path.read_text(encoding='utf-8')
                if ('point-in-time database snapshot' not in source_text or not re.search(r'COMMIT\s*;',source_text,re.I)
                    or not re.search(r'CREATE TABLE '+re.escape(fact.scope)+r'\s*\(\s*resource_id TEXT PRIMARY KEY',source_text,re.I)):
                    return False
                if fact.captured!=timestamp(row['captured_at']) or fact.observed!=fact.captured: return False
                if fact.data!={'_query_resource':fact.resource,'_query_system':fact.system}: return False
                table=raw.get(fact.scope)
                return table is not None and not any(r.get('resource_id')==fact.resource for r in table)
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
        critical=('retention_until','retained_until','legal_hold_active','shared_subjects','sole_owner')
        return any((f.system,f.resource,f.category,f.state,f.observed,f.scope)==
                   (fact.system,fact.resource,fact.category,fact.state,fact.observed,fact.scope)
                   and tokens(fact.data)<=tokens(f.data)
                   and all(fact.data.get(k)==f.data.get(k) for k in critical)
                   for f in self.reparsed[fact.source])

    def operation_veto(self,fact,operation,cutoff):
        records=self.original_rows.get((fact.source,fact.scope,fact.locator,fact.resource,fact.observed),[])
        catalog=self.activities.get(fact.data.get('_catalog_source'),{})
        return raw_operation_veto(fact,records,operation,cutoff,catalog.get('details',''))

    def review(self,audit,policy,aliases):
        validate_audit(audit,self.corpus.sources)
        self.reviewed+=1
        veto=authorization_veto(audit.case['request_text'])
        if audit.status!='NOT_APPLICABLE' and veto:
            return ['Contradicted deletion authorization: '+veto]
        try: intent=validated_decision(audit.case['request_text'],audit.intent_resolution)
        except AmbiguousIntent: intent=None
        if audit.status=='NOT_APPLICABLE':
            return [] if intent is False else ['Unsupported non-deletion verdict: authorization is not independently established']
        if intent is False: return ['Contradicted deletion verdict: request does not authorize deletion']
        if intent is None: return ['Unsupported deletion verdict: authorization is not independently established']
        cutoff=timestamp(audit.case['audit_at'])
        issues=[]
        fact_map={(f.system,f.resource):f for f in audit.facts}
        if audit.bindings:
            for key,link in audit.bindings.items():
                if not self.relationships.validates(key,link,aliases,cutoff,audit.bindings):
                    issues.append(f'Invalid identity binding: {key[0]}/{key[1]}')
                if key not in fact_map:
                    issues.append(f'Missing bound resource state: {key[0]}/{key[1]}')
        assessment=self.assess_obligations(audit,policy,aliases)
        audit.coverage_proofs=[assessment]
        issues.extend(assessment['blocking_issues'])
        for fact in audit.facts:
            if not fact.admissible(cutoff) or not self.source_supports(fact):
                issues.append(f'Unsupported source: {fact.system}/{fact.resource}/{fact.source}')
            if fact.data.get('_link_at') and timestamp(fact.data['_link_at'])>cutoff:
                issues.append(f'Future identity binding: {fact.resource}')
            if fact.state=='UNKNOWN': issues.append(f'Unproven state: {fact.resource}')
            # Check chronology and remaining physical replicas from independently
            # rebuilt source observations, without rerunning Engine selection.
            observed=[f for f in self.obligation_index.by_resource[(fact.system,fact.resource)] if f.admissible(cutoff)
                and (not f.data.get('_link_at') or timestamp(f.data['_link_at'])<=cutoff)]
            relevant=[f for f in observed if f.state!='UNKNOWN' or f.data.get('_control_observation')]
            comparable=[f for f in relevant if f.copy_role==fact.copy_role and
                (f.copy_role!='REPLICA' or f.scope==fact.scope)]
            if comparable:
                newest=max(f.observed for f in comparable)
                later=[f for f in comparable if f.observed==newest and f.observed>fact.observed]
                if any(f.state!=fact.state for f in later):
                    issues.append(f'Conflicting newer source state: {fact.system}/{fact.resource}')
            replica_scopes={f.scope for f in relevant if f.copy_role=='REPLICA'}
            for scope in replica_scopes:
                copies=[f for f in relevant if f.scope==scope]
                newest=max(f.observed for f in copies)
                if any(policy.violation(f,cutoff) for f in copies if f.observed==newest) and not policy.violation(fact,cutoff):
                    issues.append(f'Conflicting remaining replica: {fact.system}/{fact.resource}/{scope}')
            ops={s['operation'] for s in audit.steps if (s['system_id'],s['resource_id'])==(fact.system,fact.resource)}
            violation=policy.violation(fact,cutoff)
            if (fact.category=='SUPPORT_ATTACHMENT' and policy.action(fact,cutoff)=='DELETE'
                    and 'shared_subjects' in fact.data and audit.subject not in fact.data['shared_subjects']):
                issues.append(f'Unsafe deletion of another attachment owner: {fact.resource}')
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
                raw_issue=self.operation_veto(fact,step['operation'],cutoff)
                if raw_issue:issues.append('Unsafe original-source operation: '+raw_issue)
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
        if any(v.startswith(('Unsupported source:','Invalid identity binding:','Uninvestigated step resource:')) for v in issues):
            assessment['classification']='E'
        elif any(v.startswith(('Contradicted','Unsupported policy','Unsafe deletion','Conflicting')) for v in issues):
            assessment['classification']='D'
        elif issues: assessment['classification']='C'
        assessment['blocking_issues']=sorted(set(issues))
        if issues: self.challenged_cases.add(audit.case['case_id'])
        return sorted(set(issues))

    def assess_obligations(self,audit,policy,aliases):
        """The contract quantifies relevant records, not a mandatory profile step.

        A retained journal alone is neutral to deletion. Known linked obligations
        must have a readback; anonymous roots in the same admitted source remain
        a scope ambiguity and cannot be assigned by elimination. A substantive
        compliant secondary treatment can prove its obligation without inventing
        an unrelated profile. Only A/B are accepted; C/D/E remain blocking.
        """
        cutoff=timestamp(audit.case['audit_at'])
        keys={(f.system,f.resource) for f in audit.facts}
        required=self.relationships.bind(audit.subject,aliases,cutoff)
        missing=sorted(set(required)-keys)
        issues=[f'Missing bound resource state: {s}/{r}' for s,r in missing]
        kind='C' if missing else 'A'
        note='All independently bound, admissible record obligations have source-backed states.'
        if audit.status=='COMPLETE':
            if any(policy.violation(f,cutoff) for f in audit.facts):
                kind='D'; issues.append('Contradicted COMPLETE: a required treatment is violated')
            roots=[f for f in audit.facts if f.category in ('USER_PROFILE','ACCOUNT_TOMBSTONE')]
            if not roots:
                sources={f.source for f in audit.facts}
                from .relationships import declared_subjects
                unknown_roots=[f for f in self.obligation_index.facts if f.source in sources and f.admissible(cutoff)
                    and f.category in ('USER_PROFILE','ACCOUNT_TOMBSTONE') and (f.system,f.resource) not in keys
                    and not declared_subjects(f,self.relationships.known_subjects)]
                treatment=any(policy.action(f,cutoff)!='RETAIN' and not policy.violation(f,cutoff)
                              and f.state!='UNKNOWN' for f in audit.facts)
                if unknown_roots or not treatment:
                    kind='C'
                    issues.append('Unsupported COMPLETE: required deletion coverage is unproven; '+
                                  ('unbound account readbacks in admitted source' if unknown_roots else 'retention alone does not prove deletion'))
                    note='Cannot establish every relevant copy; no anonymous resource was assigned to this subject.'
                elif not issues:
                    kind='B'
                    note=('No independent admissible binding establishes a profile obligation. '
                          'The contract requires treatment of relevant records, not an extra universal profile step; '
                          'the known secondary treatment and every bound obligation are verified.')
        return {'classification':kind,'blocking_issues':sorted(set(issues)),
                'missing_bound_resources':[list(k) for k in missing],'reason':note}
