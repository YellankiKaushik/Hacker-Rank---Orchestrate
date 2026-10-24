"""Dated, explicit identity/resource links. No time-neighbor or numeric-ID joins."""
from collections import defaultdict,deque
from dataclasses import dataclass
from .models import tokens,timestamp,normalize


@dataclass(frozen=True)
class Link:
    source: str
    captured: object
    observed: object
    system: str
    resource: str
    kind: str
    locator: str
    via: tuple | None = None

    def admissible(self,cutoff):
        return self.captured<=cutoff and self.observed<=cutoff


@dataclass(frozen=True)
class Reference:
    origin: tuple
    target: tuple
    source: str
    captured: object
    observed: object
    locator: str
    registry_source: str
    registry_time: object

    def admissible(self,cutoff):
        return self.captured<=cutoff and self.observed<=cutoff and self.registry_time<=cutoff


def fact_tokens(fact):
    return fact.binding_tokens


def declared_subjects(fact,known_subjects):
    """Only subject-reference fields, never names or unrelated business prose."""
    found=set()
    def walk(data):
        if not isinstance(data,dict): return
        for key,value in data.items():
            if key in ('user_id','customer_reference','subject_reference') and isinstance(value,str):
                if value in known_subjects: found.add(value)
            elif isinstance(value,dict): walk(value)
    walk(fact.data)
    return found


class RelationshipIndex:
    def __init__(self,corpus,index):
        self.corpus,self.index=corpus,index
        self.references=[]
        self.known_subjects={r['user_id'] for r in corpus.identities}
        registry=defaultdict(list)
        owner_events={'DELETE_RECORD','UPDATE_RECORD','REDACT_RECORD','ANONYMIZE_RECORD',
                      'RETAIN_RECORD','CHECK_DATA_FLOW','DISABLE_DATA_FLOW',
                      'CHECK_RESTORE_ACCESS','BLOCK_RESTORE','INDEX_RECORD','CREATE_EXPORT'}
        for row in corpus.activities:
            if row['event_type'] in owner_events:
                registry[row['resource_id']].append((row['target_system'],timestamp(row['event_time']),row['activity_id']))
        for fact in index.facts:
            # The field explicitly identifies an upstream resource. Its owner system must
            # independently exist in dated activity metadata; the operation result is ignored.
            ref=fact.data.get('source_resource_id')
            if not isinstance(ref,str) or not ref: continue
            entries=[r for r in registry.get(ref,[]) if r[1]<=fact.observed]
            explicit_system=fact.data.get('source_system')
            owners={r[0] for r in entries}
            if explicit_system:
                entries=[r for r in entries if r[0]==explicit_system]
                owners={explicit_system} if entries else set()
            if len(owners)!=1: continue
            owner=next(iter(owners))
            entry=max((r for r in entries if r[0]==owner),key=lambda r:r[1])
            self.references.append(Reference((fact.system,fact.resource),(owner,ref),fact.source,
                fact.captured,fact.observed,fact.locator,entry[2],entry[1]))

    def bind(self,subject,aliases,cutoff):
        result={}
        for alias in sorted(aliases):
            for fact in self.index.by_token.get(alias,[]):
                if not fact.admissible(cutoff): continue
                if fact.data.get('_link_at') and timestamp(fact.data['_link_at'])>cutoff: continue
                owners=declared_subjects(fact,self.known_subjects)
                if owners and owners!={subject}:
                    raise ValueError(f'Conflicting identity binding: {fact.system}/{fact.resource} at {fact.source}')
                link=Link(fact.source,fact.captured,fact.observed,fact.system,fact.resource,
                          'EXACT_IDENTIFIER',fact.locator)
                result.setdefault((fact.system,fact.resource),link)
        for row in self.corpus.activities:
            if row['event_type']=='LINK_RESOURCE_IDENTITY' and timestamp(row['event_time'])<=cutoff and aliases & tokens(row['details']):
                key=(row['target_system'],row['resource_id'])
                result.setdefault(key,Link(row['activity_id'],timestamp(row['event_time']),timestamp(row['event_time']),
                                          *key,'CATALOG_IDENTITY',row['activity_id']))
        # Finite graph traversal: every resource is enqueued at most once, including cycles.
        adjacent=defaultdict(list)
        for ref in self.references: adjacent[ref.origin].append(ref)
        queue=deque(result)
        while queue:
            origin=queue.popleft()
            for ref in adjacent[origin]:
                if ref.target not in result and ref.admissible(cutoff):
                    result[ref.target]=Link(ref.source,ref.captured,ref.observed,*ref.target,
                        'SOURCE_RESOURCE_REFERENCE',ref.locator,ref.origin)
                    queue.append(ref.target)
        return result

    def validates(self,key,link,aliases,cutoff,all_links):
        if not link.admissible(cutoff): return False
        if link.kind=='CATALOG_IDENTITY':
            return any(r['activity_id']==link.source and (r['target_system'],r['resource_id'])==key
                       and r['event_type']=='LINK_RESOURCE_IDENTITY' and aliases & tokens(r['details'])
                       for r in self.corpus.activities)
        if link.kind=='EXACT_IDENTIFIER':
            return any(f.source==link.source and f.locator==link.locator and f.admissible(cutoff)
                       and (f.system,f.resource)==key and aliases & fact_tokens(f)
                       and (not f.data.get('_link_at') or timestamp(f.data['_link_at'])<=cutoff)
                       for f in self.index.by_resource[key])
        if link.kind=='SOURCE_RESOURCE_REFERENCE':
            return link.via in all_links and any(r.target==key and r.origin==link.via and r.source==link.source
                and r.locator==link.locator and r.admissible(cutoff) for r in self.references)
        return False
