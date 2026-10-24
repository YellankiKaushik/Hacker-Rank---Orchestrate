"""Read participant evidence into dated, source-addressable observations."""
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
import re
import sqlite3
from .models import Fact, timestamp, tokens
from .loader import contained_path
from .media import image_text, pdf_text

COLLECTIONS = {
    'customer_profiles': ('account_service','USER_PROFILE'),
    'customer_analytics_reports': ('analytics_platform','ANALYTICS_PROFILE'),
    'customer_analytics_profiles': ('analytics_platform','ANALYTICS_PROFILE'),
    'backup_catalog': ('backup_service','BACKUP_ARCHIVE'),
    'backup_restore_entries': ('backup_service','BACKUP_ARCHIVE'),
    'customer_export_jobs': ('export_service','USER_EXPORT'),
    'customer_exports': ('export_service','USER_EXPORT'),
    'connector_configurations': ('integration_service','DATA_FLOW'),
    'connector_subscriptions': ('integration_service','DATA_FLOW'),
    'customer_search_documents': ('search_service','SEARCH_INDEX_ENTRY'),
    'security_audit_events': ('security_service','SECURITY_AUDIT_LOG'),
    'security_audit_records': ('security_service','SECURITY_AUDIT_LOG'),
    'ticket_attachments': ('support_platform','SUPPORT_ATTACHMENT'),
    'support_conversations': ('support_platform','SUPPORT_MESSAGE'),
    'support_records': ('support_platform','SUPPORT_MESSAGE'),
    'retained_order_records': ('legal_archive','LEGAL_HOLD_RECORD'),
    'deleted_customer_references': ('identity_service','ACCOUNT_TOMBSTONE'),
    'customer_profiles_primary': ('account_service','USER_PROFILE'),
    'customer_profiles_failover_replica': ('account_service','USER_PROFILE'),
    'search_documents_primary': ('search_service','SEARCH_INDEX_ENTRY'),
}
DEFAULT_CATEGORY = {
    'account_service':'USER_PROFILE','analytics_platform':'ANALYTICS_PROFILE',
    'search_service':'SEARCH_INDEX_ENTRY','support_platform':'SUPPORT_MESSAGE',
    'integration_service':'DATA_FLOW','backup_service':'BACKUP_ARCHIVE',
    'export_service':'USER_EXPORT','security_service':'SECURITY_AUDIT_LOG',
    'identity_service':'ACCOUNT_TOMBSTONE','object_storage':'SUPPORT_ATTACHMENT',
    'marketing_platform':'MARKETING_PROFILE','email_delivery_service':'EMAIL_DELIVERY_LOG',
    'legal_archive':'LEGAL_HOLD_RECORD',
}
NULLS = ('', 'null', 'none', '[redacted]', 'redacted', 'no direct identifier')


def populated(value):
    return value is not None and str(value).strip().casefold() not in NULLS


def identifying(data, stable=False):
    keys = {'email','phone','email_hash','full_name','name','display_name','requester_name',
            'requester_email','requester_phone','owner_email','owner_phone','customer_email'}
    if stable:
        keys |= {'user_id','customer_reference','subject_reference'}
    for key, value in data.items():
        if key in keys and populated(value):
            return True
        if key in ('message_text','message_excerpt') and populated(value) and tokens(str(value)) != {str(value).casefold()}:
            return True
        if isinstance(value, dict) and identifying(value, stable):
            return True
    return False


def state_of(category, data):
    explicit = data.get('result') if 'record_type' in data else data.get('_state')
    if explicit:
        return {'NOT_FOUND':'ABSENT','FOUND':'PRESENT','IDENTIFIABLE':'PII'}.get(explicit, explicit)
    if data.get('status_code') == 404 or str(data.get('http_status','')) == '404':
        return 'ABSENT'
    if category == 'DATA_FLOW':
        if 'enabled' not in data: return 'UNKNOWN'
        return 'ACTIVE' if str(data.get('enabled')).lower() in ('true','1') else 'DISABLED'
    if category == 'BACKUP_ARCHIVE':
        if 'restore_allowed' not in data: return 'UNKNOWN'
        return 'ACTIVE' if str(data.get('restore_allowed')).lower() in ('true','1') else 'BLOCKED'
    if category == 'ANALYTICS_PROFILE' or category == 'PRODUCT_TELEMETRY':
        return 'PII' if identifying(data, stable=True) else 'ANONYMIZED'
    if category in ('SUPPORT_MESSAGE','EMAIL_DELIVERY_LOG','ACCOUNT_TOMBSTONE'):
        return 'PII' if identifying(data) else 'REDACTED'
    if category == 'SEARCH_INDEX_ENTRY' and 'hits' in data:
        return 'PRESENT' if data['hits']['total'] else 'ABSENT'
    return 'PRESENT'


@dataclass
class Snapshot:
    source: str
    captured: object
    observed: object
    system: str
    category: str
    scope: str
    resources: set


def restricted_sql(text):
    """Fresh in-memory DB, explicit syntax allowlist, no extensions/files/PRAGMAs."""
    if len(text) > 32_000_000:
        raise ValueError('SQL size limit exceeded')
    connection = sqlite3.connect(':memory:')
    connection.enable_load_extension(False)
    denied = {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH, sqlite3.SQLITE_ALTER_TABLE,
              sqlite3.SQLITE_DROP_TABLE, sqlite3.SQLITE_CREATE_TRIGGER, sqlite3.SQLITE_CREATE_VIEW,
              sqlite3.SQLITE_CREATE_VTABLE, sqlite3.SQLITE_PRAGMA}
    def authorize(action, arg1, arg2, db, trigger):
        if action in denied:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION and (arg2 or '').lower() not in ('json_valid',):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    connection.set_authorizer(authorize)
    budget = [0]
    def progress():
        budget[0] += 1
        return int(budget[0] > 100000)
    connection.set_progress_handler(progress, 1000)
    pending = ''
    try:
        for line in text.splitlines():
            if line.lstrip().startswith('--'):
                continue
            pending += line+'\n'
            if not sqlite3.complete_statement(pending):
                continue
            statement = pending.strip()
            pending = ''
            if re.fullmatch(r'PRAGMA\s+foreign_keys\s*=\s*ON;', statement, re.I):
                continue
            if not re.match(r'^(?:BEGIN TRANSACTION\s*;|COMMIT\s*;|CREATE TABLE\s+\w+\s*\(|CREATE INDEX\s+\w+\s+ON\s+\w+\s*\(|INSERT INTO\s+"?\w+"?\s+VALUES\s*\()', statement, re.I):
                raise ValueError('Disallowed SQL snapshot statement: '+statement[:100])
            connection.execute(statement)
        if pending.strip():
            raise ValueError('Incomplete SQL snapshot statement')
        connection.row_factory = sqlite3.Row
        names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {name: [dict(r) for r in connection.execute(f'SELECT * FROM "{name}"')] for name in names}
    finally:
        connection.close()


def log_rows(text):
    """Normalize JSON, logfmt, bracket, syslog and cloud-wrapped log dialects."""
    contexts = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        time = re.match(r'^\d{4}-\d\d-\d\dT\S+', line)
        if not time:
            continue
        payload = line[time.end():].strip()
        if payload.startswith('{'):
            data = json.loads(payload)
        else:
            payload = payload.replace('\\"','"')
            data = {k: (quoted or bare) for k, quoted, bare in
                    re.findall(r'(\w+)=(?:"([^"]*)"|([^\s"]+))', payload)}
            pipe = re.match(r'^\|\s*\w+\s*\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*(\w+)\s*\|',payload)
            if pipe:
                data.setdefault('service',pipe[1]); data.setdefault('trace_id',pipe[2].strip()); data.setdefault('event',pipe[3])
            bracket = re.search(r'\[\w+\]\s+\[([^]]+)\]\s+\[([^]]+)\]\s+(\w+):', payload)
            if bracket:
                data.setdefault('service',bracket[1]); data.setdefault('event',bracket[3])
                data.setdefault('trace_id',bracket[2])
            syslog = re.search(r'<\d+>1\s+\S+\s+(\S+)\s+(\S+)\s+- -', payload)
            if syslog:
                data.setdefault('service',syslog[1]); data.setdefault('trace_id',syslog[2])
            data.setdefault('service',data.get('function',''))
            data.setdefault('trace_id',data.get('requestId',''))
        trace = data.get('trace_id','')
        if trace:
            previous = contexts.setdefault(trace,{})
            previous.update({k:v for k,v in data.items() if k in ('lookup_key','match_key','subject_key','scan_key','owner_key','subject_ref','resource_id','customer_reference')})
            data = {**previous, **data}
        yield time[0], data, lineno


class EvidenceIndex:
    def __init__(self, corpus, cache_dir=None):
        self.facts = []
        self.snapshots = []
        self.media = {}
        self.coverage = defaultdict(int)
        self.cache_dir = cache_dir
        self.source_hashes = {}
        for source in corpus.manifest:
            path = contained_path(corpus.root,source['file_path'])
            self.source_hashes[source['file_id']] = hashlib.sha256(path.read_bytes()).hexdigest()
            source = {**source, '_captured':timestamp(source['captured_at'])}
            extension = path.suffix
            if extension == '.json': self.json(source,json.loads(path.read_text(encoding='utf-8')))
            elif extension == '.sql': self.sql(source,restricted_sql(path.read_text(encoding='utf-8')))
            elif extension == '.log': self.logs(source,path.read_text(encoding='utf-8'))
            elif extension == '.txt': self.text(source,path.read_text(encoding='utf-8'))
            elif extension in ('.pdf','.png'):
                text = pdf_text(path) if extension == '.pdf' else image_text(path,cache_dir)
                self.media[source['file_id']] = text
            else: raise ValueError(f'Unsupported evidence extension {extension}')
            self.coverage[extension] += 1
        self.link_documents(corpus)
        self.activity_observations(corpus)
        self.by_resource = defaultdict(list)
        self.by_token = defaultdict(list)
        for fact in self.facts:
            self.by_resource[(fact.system,fact.resource)].append(fact)
            for token in tokens(fact.data.get('_bindings',fact.data)):
                self.by_token[token].append(fact)

    def add(self, source, system, resource, category, data, observed=None, scope='', locator=''):
        if not resource or not system or not category:
            raise ValueError('Missing observation scope')
        if str(data.get('account_status','')).upper() == 'DELETED' and category == 'USER_PROFILE':
            category = 'ACCOUNT_TOMBSTONE'
        self.facts.append(Fact(source['file_id'],source['_captured'],
            timestamp(observed) if isinstance(observed,str) else observed or source['_captured'],
            system,resource,category,state_of(category,data),data,scope,locator))

    def records(self, source, records, system, category, observed, scope):
        for i,record in enumerate(records):
            self.add(source,record.get('system',system),record['resource_id'],
                     record.get('record_type',category),record,
                     record.get('observed_at',record.get('recorded_at',observed)),scope,str(i))

    def json(self, source, doc):
        if 'snapshots' in doc:
            for i,snapshot in enumerate(doc['snapshots']):
                collection = snapshot['collection']
                category = COLLECTIONS.get(collection,('', ''))[1]
                self.records(source,snapshot['records'],snapshot['data_store'],category,snapshot['captured_at'],f'json/{i}/{collection}')
        elif 'service_exports' in doc:
            for system, groups in doc['service_exports'].items():
                for group, records in groups.items():
                    self.records(source,records,system,DEFAULT_CATEGORY[system],doc['exported_at'],f'json/{system}/{group}')
        elif 'records' in doc:
            category = COLLECTIONS.get(doc.get('collection',''),('', ''))[1]
            system = COLLECTIONS.get(doc.get('collection',''),(doc.get('source',''), ''))[0]
            self.records(source,doc['records'],system,category,doc.get('captured_at',doc.get('exported_at')), 'json/records')

    def sql(self, source, tables):
        for name, rows in tables.items():
            if name == 'snapshot_scope': continue
            if name.startswith('customer_data_'):
                grouped = defaultdict(set)
                for row in rows:
                    category = COLLECTIONS[row['collection_name']][1]
                    data = json.loads(row['record_json'])
                    self.add(source,row['origin_system'],row['resource_id'],category,data,
                             source['_captured'],name,row['resource_id'])
                    grouped[(row['origin_system'],category)].add(row['resource_id'])
                for (system,category),resources in grouped.items():
                    self.snapshots.append(Snapshot(source['file_id'],source['_captured'],source['_captured'],system,category,name,resources))
            else:
                if name not in COLLECTIONS:
                    raise ValueError(f'Unknown SQL collection: {name}')
                system,category = COLLECTIONS[name]
                for row in rows:
                    self.add(source,system,row['resource_id'],category,row,source['_captured'],name,row['resource_id'])
                self.snapshots.append(Snapshot(source['file_id'],source['_captured'],source['_captured'],system,category,name,{r['resource_id'] for r in rows}))

    def logs(self, source, text):
        for time,data,line in log_rows(text):
            event = data.get('event','')
            resource = data.get('resource_id')
            system = data.get('system',data.get('service',''))
            if not resource: continue
            category = data.get('record_type',DEFAULT_CATEGORY.get(system,''))
            state = None
            if event in ('profile_lookup_completed','contact_lookup_completed','contact_query_completed'):
                state = 'ABSENT' if str(data.get('rows')) == '0' else 'PRESENT'
                if event.startswith('contact_'):
                    category = 'SECONDARY_IDENTIFIER'; system = 'support_platform' if system=='support_replica' else system
            elif event == 'index_query_completed': state = 'PRESENT' if data.get('result')=='hit' else 'ABSENT'
            elif event in ('analytics_identity_scan','message_pii_scan'): state = 'PII'
            elif event == 'analytics_profile_read': state = 'ANONYMIZED' if str(data.get('direct_identifiers'))=='0' else 'PII'
            elif event == 'analytics_profile_read_completed': state = state_of('ANALYTICS_PROFILE',data)
            elif event in ('attachment_pii_scan','export_download_check_completed','export_metadata_read_completed'):
                state = 'PRESENT'; category = 'SUPPORT_ATTACHMENT' if event=='attachment_pii_scan' else 'USER_EXPORT'
            elif event in ('connector_heartbeat','connector_config_loaded','connector_config_read_completed'):
                state = 'ACTIVE' if data.get('enabled')=='true' else 'DISABLED'
            elif event == 'restore_candidate_evaluated': state = 'ACTIVE' if data.get('eligible')=='true' else 'BLOCKED'
            elif event == 'restore_authorization_completed': state = 'BLOCKED' if data.get('decision')=='deny' else 'ACTIVE'
            elif event == 'restore_policy_read_completed': state = 'ACTIVE' if data.get('restore_allowed')=='true' else 'BLOCKED'
            elif event == 'audit_record_read_completed': state = 'PRESENT' if str(data.get('rows'))=='1' else 'ABSENT'
            elif event in ('message_read','support_ticket_read_completed'): state = state_of('SUPPORT_MESSAGE',data)
            elif event == 'record_lookup': state = state_of(category,data)
            if state and category:
                self.add(source,system,resource,category,{**data,'_state':state},time,'log',f'line:{line}')

    def text(self, source, text):
        for i,line in enumerate(text.splitlines()):
            parts = [p.strip() for p in line.removeprefix('- ').split('|')]
            if len(parts)==6 and re.match(r'^\d{4}-',parts[0]):
                time,system,resource,category,result,subject = parts
                self.add(source,system,resource,category,{'record_type':category,'result':result,'subject_reference':subject},time,'handover',f'line:{i+1}')

    def link_documents(self, corpus):
        sources = {r['file_id']:{**r,'_captured':timestamp(r['captured_at'])} for r in corpus.manifest}
        for row in corpus.activities:
            if row['event_type'] != 'LINK_RESOURCE_IDENTITY': continue
            reference = re.search(r'\(([^)]+)\)',row['details'])
            reference = reference[1] if reference else row['resource_id']
            uid = re.search(r'\buser_\d+\b',row['details'])
            for source_id,text in self.media.items():
                folded = re.sub(r'\s+',' ',text).casefold()
                # Catalog display label joins the media to a resource; numeric suffixes never do.
                label = reference.casefold()
                if label not in folded and row['resource_id'].casefold() not in folded:
                    continue
                system = row['target_system']
                # A shared subject ID in an unrelated document does not identify this resource.
                if re.fullmatch(r'user_\d+',label) and 'reference registry' not in folded:
                    continue
                category = DEFAULT_CATEGORY.get(system)
                if not category: continue
                state = 'PRESENT'
                if category in ('ANALYTICS_PROFILE','PRODUCT_TELEMETRY','SUPPORT_MESSAGE'): state='PII'
                elif category == 'DATA_FLOW':
                    state = 'ACTIVE' if 'continuous' in folded and ('delivered' in folded or 'events/hour' in folded) else 'UNKNOWN'
                elif category == 'BACKUP_ARCHIVE': state = 'UNKNOWN'
                elif category == 'ACCOUNT_TOMBSTONE':
                    state = 'PII' if re.search(r'[\w.+-]+@[\w.-]+\.[a-z]+',folded) else 'REDACTED'
                data = {'_state':state,'_content':text,'_link_at':row['event_time'],
                        '_catalog_source':row['activity_id'],'subject_reference':uid[0] if uid else '',
                        '_bindings':[uid[0] if uid else '',row['details']],
                        '_link_details':row['details']}
                self.add(sources[source_id],system,row['resource_id'],category,data,scope='media',locator='catalog-grounded media')
        # A document explicitly names a record and subject without needing a catalog join.
        for source_id,text in self.media.items():
            if 'support reference' in text.casefold() and 'uploader customer' in text.casefold():
                resource = re.search(r'\bsupport_\d+\b',text)
                if resource:
                    self.add(sources[source_id],'support_platform',resource[0],'SUPPORT_ATTACHMENT',{'_content':text,'_state':'PRESENT'},scope='media',locator='support attachment')

    def activity_observations(self, corpus):
        # Operational success is not readback proof. Only explicit status/access checks qualify.
        for row in corpus.activities:
            state = None
            category = DEFAULT_CATEGORY.get(row['target_system'])
            if row['event_type']=='CHECK_DATA_FLOW' and 'remains enabled' in row['details']:
                state='ACTIVE'
            if row['event_type']=='CHECK_RESTORE_ACCESS' and 'can still be restored' in row['details']:
                state='ACTIVE'
            if state:
                self.add({'file_id':row['activity_id'],'_captured':timestamp(row['event_time'])},
                         row['target_system'],row['resource_id'],category,
                         {'_state':state,'_content':row['details']},scope='readback activity',locator=row['activity_id'])
