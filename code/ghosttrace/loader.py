import csv
from pathlib import Path
from .models import timestamp

SCHEMAS = {
    'deletion_requests.csv': 'case_id,email,requested_at,reported_status,reported_at,audit_at,request_text',
    'sample_deletion_requests.csv': 'case_id,email,requested_at,reported_status,reported_at,audit_at,request_text',
    'user_identities.csv': 'user_id,name,email,phone,email_hash,updated_at',
    'user_audit_log.csv': 'audit_id,user_id,event_time,field_name,old_value,new_value',
    'system_activity.csv': 'activity_id,event_time,event_type,source_system,target_system,resource_id,reported_result,details',
    'deletion_rules.csv': 'rule_id,data_category,condition,required_action',
    'evidence_files.csv': 'file_id,file_path,origin,captured_at',
}


def read_csv(path, expected=None):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        schema = expected or SCHEMAS.get(Path(path).name)
        if schema and reader.fieldnames != schema.split(','):
            raise ValueError(f'Invalid CSV schema: {Path(path).name}: {reader.fieldnames}')
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f'Malformed CSV row: {Path(path).name}')
    if rows and schema:
        key = schema.split(',')[0]
        if len({r[key] for r in rows}) != len(rows):
            raise ValueError(f'Duplicate key {key}: {Path(path).name}')
    return rows


def contained_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Evidence path escapes participant dataset')
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size > 32_000_000:
        raise ValueError('Evidence exceeds 32 MB safety limit')
    return path


class Corpus:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.identities = read_csv(self.root/'user_identities.csv')
        self.history = read_csv(self.root/'user_audit_log.csv')
        self.activities = read_csv(self.root/'system_activity.csv')
        self.rules = read_csv(self.root/'deletion_rules.csv')
        self.manifest = read_csv(self.root/'evidence_files.csv')
        self.sources = {r['file_id']: timestamp(r['captured_at']) for r in self.manifest}
        self.sources.update({r['activity_id']: timestamp(r['event_time']) for r in self.activities})
        self.sources.update({r['audit_id']: timestamp(r['event_time']) for r in self.history})
        for row in self.manifest:
            contained_path(self.root, row['file_path'])
