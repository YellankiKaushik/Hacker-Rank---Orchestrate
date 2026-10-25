"""Independent authored authorization/raw-field/official-plan regressions."""
import copy
import csv
import json
from dataclasses import replace
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from test_core import ROOT,CASE,IDENTITY,EARLY,CUTOFF,RULES
from ghosttrace.adapters import EvidenceIndex,state_of
from ghosttrace.engine import Engine
from ghosttrace.reviewer import GhostGuard
from ghosttrace.intent import deletion_intent,AmbiguousIntent
from independent_contract import check
from ghosttrace.invariants import raw_operation_veto

class Phase2Tests(unittest.TestCase):
    def environment(self,folder,record=None):
        record=record or {'system':'identity_service','resource_id':'fixture_tombstone','record_type':'ACCOUNT_TOMBSTONE','result':'REDACTED','subject_reference':IDENTITY['user_id']}
        source={'file_id':'fixture','file_path':'records.json','captured_at':EARLY.isoformat()}
        (folder/'records.json').write_text(json.dumps({'records':[{'recorded_at':EARLY.isoformat(),**record}]}),encoding='utf-8')
        c=SimpleNamespace(root=folder,manifest=[source],activities=[],history=[],identities=[IDENTITY],rules=RULES,sources={'fixture':EARLY})
        return c,EvidenceIndex(c)
    def test_negation_and_information_real_source_end_to_end(self):
        texts=['I am not requesting deletion; please send a copy of my personal data.',
          'Could you explain deletion?','Please describe the erasure process for my account.',
          'I am not authorizing account erasure. Send my records instead.',
          'I am not asking you to erase my account. Export my records.',
          'Should I delete my account?',
          'Please unsubscribe me from promotional emails.',
          'Please suspend my account temporarily.','I only want information about deleting my account.',
          'Please change my email address. I want to continue using the service.']
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            c,i=self.environment(Path(d));e=Engine(c,i);g=GhostGuard(c,i)
            for text in texts:
                with self.subTest(text=text):
                    a=e.investigate({**CASE,'request_text':text});self.assertEqual((a.status,a.steps),('NOT_APPLICABLE',[]))
                    self.assertEqual(g.review(a,e.policy,set()),[])
    def test_positive_directives_and_retention_exceptions(self):
        for text in ['Delete my account, but do not delete invoices required by law.',
                     'Explain your retention policy. Please erase my profile.',
                     'Please suspend my account temporarily. Also erase my profile.',
                     'I am requesting erasure of my personal data.',
                     'Please process a permanent account-deletion request.',
                     'Please begin the deletion process for my account.',
                     'Please investigate and finish the deletion.',
                     'I updated my account email before deleting it. Please check no old records remain.',
                     'Please permanently delete my account.']:
            with self.subTest(text=text):self.assertTrue(deletion_intent(text))
    def test_unframed_or_ambiguous_mention_abstains(self):
        for text in ['Deletion','Something about erasure','Can you look into this?','I am considering deleting my account.']:
            with self.subTest(text=text),self.assertRaises(AmbiguousIntent):deletion_intent(text)
    def test_compliant_label_never_overrides_direct_fields(self):
        for category,label,field in [('ACCOUNT_TOMBSTONE','REDACTED','email'),('ACCOUNT_TOMBSTONE','REDACTED','phone'),('ANALYTICS_PROFILE','ANONYMIZED','email'),('ANALYTICS_PROFILE','ANONYMIZED','user_id')]:
            with self.subTest(category=category,field=field):
                self.assertEqual(state_of(category,{'record_type':category,'result':label,field:'fictional-value'}),'PII')
    def test_nested_arrays_and_nulls(self):
        self.assertEqual(state_of('ACCOUNT_TOMBSTONE',{'record_type':'ACCOUNT_TOMBSTONE','result':'REDACTED','payload':[{'phone':'fictional-phone'}]}),'PII')
        self.assertEqual(state_of('ACCOUNT_TOMBSTONE',{'record_type':'ACCOUNT_TOMBSTONE','result':'REDACTED','user_id':'subject_fixture','email':None,'phone':'[redacted]','email_hash':''}),'REDACTED')
    def test_real_exposed_tombstone_has_finding_remedy_check_and_diagnostic(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            record={'system':'identity_service','resource_id':'fixture_tombstone','record_type':'ACCOUNT_TOMBSTONE','result':'REDACTED','subject_reference':IDENTITY['user_id'],'email':IDENTITY['email']}
            c,i=self.environment(Path(d),record);e=Engine(c,i);a=e.investigate(CASE)
            self.assertEqual(a.status,'INCOMPLETE');self.assertEqual([s['operation'] for s in a.steps],['REPORT_EXPOSED_PII','REDACT_RECORD','VERIFY_RECORD_REDACTED'])
            self.assertIn('_state_contradiction',a.facts[0].data)
            self.assertEqual(GhostGuard(c,i).review(a,e.policy,{IDENTITY['user_id'],IDENTITY['email']}),[])
    def test_guard_detects_correlated_wrong_primary_state_from_original_fields(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            record={'system':'identity_service','resource_id':'fixture_tombstone','record_type':'ACCOUNT_TOMBSTONE','result':'REDACTED','subject_reference':IDENTITY['user_id'],'email':IDENTITY['email']}
            # Both primary and secondary parser are deliberately wrong. The
            # original-value invariant must still veto their shared conclusion.
            with patch('ghosttrace.adapters.state_of',return_value='REDACTED'):
                c,i=self.environment(Path(d),record);e=Engine(c,i);a=e.investigate(CASE);g=GhostGuard(c,i)
                self.assertEqual(a.status,'COMPLETE');self.assertFalse(g.source_supports(a.facts[0]))
                self.assertTrue(g.review(a,e.policy,{IDENTITY['user_id'],IDENTITY['email']}))
    def test_guard_vetoes_correlated_authorization_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            c,i=self.environment(Path(d));e=Engine(c,i);a=e.investigate(CASE)
            a.case={**CASE,'request_text':'I am not requesting account deletion. Send a copy.'}
            with patch('ghosttrace.reviewer.validated_decision',return_value=True):
                self.assertTrue(any('authorization' in v for v in GhostGuard(c,i).review(a,e.policy,{IDENTITY['user_id']})))
    def test_analytics_nested_attribution_real_source(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            record={'system':'analytics_platform','resource_id':'analytics_fixture','record_type':'ANALYTICS_PROFILE','result':'ANONYMIZED','subject_reference':IDENTITY['user_id'],'payload':[{'user_id':IDENTITY['user_id']}]}
            c,i=self.environment(Path(d),record);e=Engine(c,i);a=e.investigate(CASE)
            self.assertEqual(a.status,'INCOMPLETE');self.assertIn('ANONYMIZE_RECORD',[s['operation'] for s in a.steps])
            self.assertEqual(GhostGuard(c,i).review(a,e.policy,{IDENTITY['user_id']}),[])
    def test_guard_original_controls_reject_correlated_blocked_claim(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            record={'system':'backup_service','resource_id':'archive_fixture','record_type':'BACKUP_ARCHIVE','result':'BLOCKED','restore_allowed':True,'subject_reference':IDENTITY['user_id']}
            with patch('ghosttrace.adapters.state_of',return_value='BLOCKED'):
                c,i=self.environment(Path(d),record);self.assertFalse(GhostGuard(c,i).source_supports(i.facts[0]))
    def test_guard_original_positive_readback_rejects_correlated_absence(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            record={'system':'account_service','resource_id':'profile_fixture','record_type':'USER_PROFILE','result':'FOUND','subject_reference':IDENTITY['user_id']}
            with patch('ghosttrace.adapters.state_of',return_value='ABSENT'):
                c,i=self.environment(Path(d),record);self.assertFalse(GhostGuard(c,i).source_supports(i.facts[0]))
    def test_independent_ownership_retention_and_tombstone_operation_vetoes(self):
        from test_core import fact
        self.assertTrue(raw_operation_veto(fact(category='SUPPORT_ATTACHMENT'),[{'uploaded_by':IDENTITY['user_id']}],'DELETE_RECORD',CUTOFF))
        self.assertTrue(raw_operation_veto(fact(category='SECURITY_AUDIT_LOG'),[{'retention_until':'2027-01-01T00:00:00Z'}],'DELETE_RECORD',CUTOFF))
        self.assertTrue(raw_operation_veto(fact(category='ACCOUNT_TOMBSTONE'),[],'DELETE_RECORD',CUTOFF))
        self.assertEqual(raw_operation_veto(fact(category='DATA_FLOW',state='ACTIVE'),[{'record_type':'DATA_FLOW','result':'ACTIVE'}],'VERIFY_DATA_FLOW_DISABLED',CUTOFF),'')
    def test_unrelated_neighbor_does_not_contaminate_target(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            folder=Path(d);c,i=self.environment(folder)
            doc=json.loads((folder/'records.json').read_text());doc['records'].append({**doc['records'][0],'resource_id':'neighbor','subject_reference':'other_subject','email':'other@example.invalid'})
            (folder/'records.json').write_text(json.dumps(doc));i=EvidenceIndex(c);e=Engine(c,i);a=e.investigate(CASE)
            self.assertEqual(a.status,'COMPLETE');self.assertEqual(GhostGuard(c,i).review(a,e.policy,{IDENTITY['user_id']}),[])
    def test_independent_checker_reports_all_missing_phase_cases(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            folder=Path(d);cases=[{**CASE,'case_id':str(n)} for n in range(3)]
            with (folder/'cases.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(CASE));w.writeheader();w.writerows(cases)
            with (folder/'output.csv').open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['case_id','deletion_status','steps_json']);w.writeheader()
                for c in cases:w.writerow({'case_id':c['case_id'],'deletion_status':'INCOMPLETE','steps_json':'[]'})
            result=check(folder/'output.csv',folder/'cases.csv')
            self.assertEqual(result['SHAPE_VALID'],'PASS');self.assertEqual(result['COMPLETE_PLAN_CONTRACT_VALID'],'FAIL')
            self.assertEqual(result['invalid_case_ids'],['0','1','2'])

if __name__=='__main__':unittest.main()
