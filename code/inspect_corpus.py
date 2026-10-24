"""Developer inspection of schemas and event vocabulary, not labels."""
from pathlib import Path
from collections import Counter
import re
import json

if __name__ == '__main__':
    counts, examples = Counter(), {}
    for path in Path('dataset/evidence/logs').glob('*.log'):
        for line in path.read_text().splitlines():
            if '{' in line:
                try:
                    ev = json.loads(line[line.index('{'):]).get('event', '')
                except ValueError:
                    continue
            else:
                match = re.search(r'event=([^ ]+)', line)
                ev = match[1] if match else ''
            counts[ev] += 1
            examples.setdefault(ev, line)
    for key in sorted(counts):
        print(key, counts[key], examples[key][:520])
