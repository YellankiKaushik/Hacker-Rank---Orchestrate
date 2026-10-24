"""Controlled ambiguous-intent assessment; live metrics are never replaced by mocks."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ghosttrace.intent import deletion_intent,AmbiguousIntent

ROOT=Path(__file__).resolve().parents[2]
FIXTURES=[
    ('I do not want to delete my account.',False),
    ('Please delete my account, but do not delete legally retained invoices.',True),
    ('Please explain the deletion policy for my account.',False),
    ('No quiero eliminar mi cuenta.',False),
    ('Ne supprimez pas mon compte.',False),
    ('Não quero excluir minha conta.',False),
    ('Bitte löschen Sie mein Konto nicht.',False),
    ('不要删除我的账户。',False),
    ('アカウントを削除しないでください。',False),
    ('アカウントの削除を依頼します。',True),
    ('Solicito a exclusão permanente da conta.',True),
    ('Borra mi cuenta y mis datos personales.',True),
    ('I withdraw my consent to retain my personal profile; please dispose of it.',True),
    ('Please put this on ice while I consider my privacy options.',None),
]


def evaluate():
    correct=unresolved=unambiguous_correct=unambiguous=0; details=[]
    for text,expected in FIXTURES:
        try: predicted=deletion_intent(text)
        except AmbiguousIntent: predicted=None; unresolved+=1
        correct+=predicted==expected
        if expected is not None:
            unambiguous+=1; unambiguous_correct+=predicted==expected
        details.append({'text':text,'expected':expected,'deterministic':predicted})
    probe_path=ROOT/'artifacts/ai_access_probe.json'
    probe=json.loads(probe_path.read_text()) if probe_path.exists() else {'available':False,'reason':'probe not recorded'}
    result={'fixtures':len(FIXTURES),'deterministic_correct':correct,'deterministic_unresolved':unresolved,
        'unambiguous_fixtures':unambiguous,'unambiguous_correct':unambiguous_correct,
        'live_ai_quality':'NOT VERIFIED','live_ai_reason':probe.get('reason','no validated model/pricing configuration'),
        'live_inference_calls':0,'details':details,
        'mock_contract_results_are_not_live_benchmarks':True}
    target=ROOT/'tmp/ai_controlled_evaluation.json'; target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    return result


if __name__=='__main__':
    print(json.dumps({k:v for k,v in evaluate().items() if k!='details'},indent=2))
