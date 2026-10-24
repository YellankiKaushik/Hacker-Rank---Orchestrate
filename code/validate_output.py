"""Independent final artifact validator; no inference and no sample-answer access."""
import argparse
from pathlib import Path
from ghosttrace.loader import Corpus,read_csv
from ghosttrace.validator import validate_file
from ghosttrace.semantic_validation import validate_semantic_file

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=root/'dataset')
    parser.add_argument('--requests',type=Path)
    parser.add_argument('--output',type=Path,default=root/'output.csv')
    args=parser.parse_args()
    corpus=Corpus(args.dataset)
    cases=read_csv(args.requests or args.dataset/'deletion_requests.csv')
    count=validate_semantic_file(args.output,cases,corpus,args.dataset.parent/'tmp/ocr')
    print(f'Validated {count} sorted cases, schema, source/observation times, source states, identity bindings and policy.')
