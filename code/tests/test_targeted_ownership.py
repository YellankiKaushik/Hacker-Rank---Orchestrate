"""Policy authorization scenarios independent of sample answers and resource IDs."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from test_core import ROOT,IDENTITY,EARLY,CUTOFF,CASE,RULES,fact,fake_environment
from ghosttrace.policy import attachment_ownership,Policy
from ghosttrace.engine import Engine
from ghosttrace.adapters import EvidenceIndex
from ghosttrace.reviewer import GhostGuard


class OwnershipSemanticsTests(unittest.TestCase):
    def test_partial_singleton_and_duplicate_entries_never_prove_exclusivity(self):
        for owners in [['subject_alpha'],['subject_alpha','subject_alpha']]:
            data={'email':'alex@example.test','shared_subjects':owners}
            self.assertEqual(attachment_ownership(data),'UNKNOWN')
            c,i=fake_environment([replace(fact(category='SUPPORT_ATTACHMENT'),data=data)])
            with self.assertRaisesRegex(ValueError,'Unresolved state'): Engine(c,i).investigate(CASE)
            a=Engine(c,i).investigate(CASE,permit_partial=True)
            self.assertEqual((a.status,a.steps),('INCOMPLETE',[]))

    def test_explicit_exclusivity_permits_sole_action_but_conflicts_abstain(self):
        for data in [{'sole_owner':True,'shared_subjects':['subject_alpha']},
                     {'_link_details':'Attachment belongs only to subject_alpha; no other subject is linked.'}]:
            self.assertEqual(attachment_ownership(data),'SOLE')
            self.assertEqual(Policy(RULES).action(replace(fact(category='SUPPORT_ATTACHMENT'),data=data),CUTOFF),'DELETE')
        for data in [{'sole_owner':True,'shared_subjects':['subject_alpha','subject_beta']},
                     {'sole_owner':None,'shared_subjects':['subject_alpha']},
                     {'sole_owner':False,'_link_details':'belongs only to subject_alpha; no other subject is linked'}]:
            self.assertEqual(attachment_ownership(data),'UNKNOWN')

    def test_shared_lower_bound_is_not_a_policy_redaction_authorization(self):
        data={'shared_subjects':['subject_alpha','subject_beta']}
        self.assertEqual(attachment_ownership(data),'SHARED')
        f=replace(fact(category='SUPPORT_ATTACHMENT'),data=data)
        self.assertEqual(Policy(RULES).action(f,CUTOFF),'UNKNOWN')
        explicit=[{**r,'required_action':'REDACT','condition':'Always'} if r['data_category']=='SUPPORT_ATTACHMENT' else r for r in RULES]
        self.assertEqual(Policy(explicit).action(f,CUTOFF),'REDACT')

    def test_original_source_reread_rejects_invented_boolean_sole_owner(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            folder=Path(d); source={'file_id':'fixture','file_path':'attachment.json','captured_at':EARLY.isoformat()}
            (folder/'attachment.json').write_text(json.dumps({'records':[{'recorded_at':EARLY.isoformat(),
                'system':'support_platform','resource_id':'attachment','record_type':'SUPPORT_ATTACHMENT',
                'result':'FOUND','subject_reference':'subject_alpha','shared_subjects':['subject_alpha']}]}))
            c=SimpleNamespace(root=folder,manifest=[source],activities=[],identities=[IDENTITY],history=[],rules=RULES)
            i=EvidenceIndex(c); g=GhostGuard(c,i); original=i.facts[0]
            self.assertTrue(g.source_supports(original))
            self.assertFalse(g.source_supports(replace(original,data={**original.data,'sole_owner':True})))


if __name__=='__main__': unittest.main()
