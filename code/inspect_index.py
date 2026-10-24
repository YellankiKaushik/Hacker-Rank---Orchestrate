from pathlib import Path
import json
from ghosttrace.loader import Corpus
from ghosttrace.adapters import EvidenceIndex

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    corpus = Corpus(root/'dataset')
    index = EvidenceIndex(corpus, root/'tmp/ocr')
    (root/'tmp/media_text.json').write_text(json.dumps(index.media, ensure_ascii=False, indent=2), encoding='utf-8')
    print('facts', len(index.facts), 'snapshot scopes', len(index.snapshots), 'formats', dict(index.coverage))
    for source, text in index.media.items():
        print(source, text[:300].replace('\n',' | '))
