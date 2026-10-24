"""Read-only participant corpus census; never loads sample answers into inference."""
from pathlib import Path
from collections import Counter
import csv
import json

ROOT = Path(__file__).resolve().parents[1]


def census(root=ROOT / 'dataset'):
    result = {}
    for path in sorted(root.glob('*.csv')):
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            result[path.name] = {'rows': len(rows), 'columns': reader.fieldnames}
            if path.name == 'system_activity.csv':
                result[path.name]['event_types'] = dict(Counter(r['event_type'] for r in rows))
            if path.name == 'user_audit_log.csv':
                result[path.name]['fields'] = dict(Counter(r['field_name'] for r in rows))
    result['evidence_formats'] = dict(Counter(p.suffix for p in (root/'evidence').rglob('*') if p.is_file()))
    return result


if __name__ == '__main__':
    print(json.dumps(census(), indent=2))
