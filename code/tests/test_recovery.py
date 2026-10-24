"""Independent source-linkage, review and optional-provider regression scenarios."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import json
import os
import tempfile
import unittest
import urllib.error
from test_core import ROOT,EARLY,CUTOFF,LATE,CASE,IDENTITY,RULES,fact,fake_environment
from ghosttrace.models import tokens
from ghosttrace.identity import IdentityGraph
from ghosttrace.engine import Engine
from ghosttrace.intent import deletion_intent,AmbiguousIntent
from ghosttrace.adapters import Snapshot,EvidenceIndex
from ghosttrace.reviewer import GhostGuard,rejection_category
from ghosttrace.relationships import RelationshipIndex
from ghosttrace.ai import AIConfig,IntentAI


class RelationshipRecoveryTests(unittest.TestCase):
    def environment(self):
        child=replace(fact('search_alpha','search_service','SEARCH_INDEX_ENTRY'),
            data={'email':'alex@example.test','source_resource_id':'old_profile'},scope='search_documents_primary')
        corpus,index=fake_environment([child])
        corpus.activities=[{'activity_id':'operation_alpha','event_time':EARLY.isoformat(),
            'event_type':'DELETE_RECORD','target_system':'account_service','source_system':'worker',
            'resource_id':'old_profile','reported_result':'FAILED','details':'Operation result is a claim.'}]
        return corpus,index

    def test_reference_recovers_non_numeric_resource_identity(self):
        c,i=self.environment(); links=RelationshipIndex(c,i).bind('subject_alpha',{'alex@example.test'},CUTOFF)
        link=links['account_service','old_profile']
        self.assertEqual(link.kind,'SOURCE_RESOURCE_REFERENCE')
        self.assertEqual(link.via,('search_service','search_alpha'))

    def test_failed_operation_can_supply_scope_but_not_absence(self):
        c,i=self.environment(); result=Engine(c,i).investigate(CASE)
        self.assertNotIn('old_profile',[f.resource for f in result.facts])
        self.assertTrue(any('no admissible state' in issue for issue in result.issues))

    def test_reference_plus_exhaustive_capture_proves_scoped_absence(self):
        c,i=self.environment()
        i.snapshots=[Snapshot('table_capture',EARLY,EARLY,'account_service','USER_PROFILE',
                              'customer_profiles_primary',set(),True)]
        result=Engine(c,i).investigate(CASE)
        parent=next(f for f in result.facts if f.resource=='old_profile')
        self.assertEqual(parent.state,'ABSENT'); self.assertEqual(parent.source,'table_capture')
        self.assertEqual(parent.locator,'scoped inventory absence')

    def test_unrelated_inventory_cannot_clear_existing_profile(self):
        c,i=fake_environment([fact()])
        i.snapshots=[Snapshot('unrelated_batch',CUTOFF,CUTOFF,'account_service','USER_PROFILE',
                              'customer_profiles',set(),False)]
        self.assertEqual(Engine(c,i).investigate(CASE).status,'INCOMPLETE')

    def test_nonexhaustive_unrelated_batch_does_not_prove_referenced_absence(self):
        c,i=self.environment()
        i.snapshots=[Snapshot('unrelated_batch',EARLY,EARLY,'account_service','USER_PROFILE',
                              'customer_profiles',set(),False)]
        result=Engine(c,i).investigate(CASE)
        self.assertNotIn('old_profile',[f.resource for f in result.facts])

    def test_future_registry_event_cannot_bind_reference(self):
        c,i=self.environment(); c.activities[0]['event_time']=LATE.isoformat()
        links=RelationshipIndex(c,i).bind('subject_alpha',{'alex@example.test'},CUTOFF)
        self.assertNotIn(('account_service','old_profile'),links)

    def test_same_numeric_suffix_is_not_a_relationship(self):
        c,i=fake_environment([fact('search_77','search_service','SEARCH_INDEX_ENTRY')])
        links=RelationshipIndex(c,i).bind('subject_alpha',{'alex@example.test'},CUTOFF)
        self.assertNotIn(('account_service','account_77'),links)

    def test_conflicting_stable_subject_does_not_join_on_email(self):
        other={**IDENTITY,'user_id':'subject_beta','email':'beta@example.test'}
        conflict=replace(fact(),data={'email':'alex@example.test','customer_reference':'subject_beta'})
        c,i=fake_environment([conflict]); c.identities.append(other)
        with self.assertRaisesRegex(ValueError,'Conflicting identity binding'): Engine(c,i).investigate(CASE)

    def test_historical_phone_format_variants_are_linked(self):
        identity={**IDENTITY,'phone':'+44 7700 900123'}
        graph=IdentityGraph([identity],[])
        _,aliases=graph.resolve('alex@example.test',CUTOFF)
        self.assertTrue(aliases & tokens({'lookup_key':'+44-7700-900123'}))
        self.assertFalse(aliases & tokens({'lookup_key':'+44-7700-900124'}))

    def test_ocr_separator_normalization_requires_real_catalog_reference(self):
        source={'file_id':'screen_alpha','captured_at':EARLY.isoformat()}
        c=SimpleNamespace(manifest=[source],activities=[{'activity_id':'catalog_alpha',
            'event_type':'LINK_RESOURCE_IDENTITY','event_time':EARLY.isoformat(),
            'target_system':'identity_service','resource_id':'tomb_alpha',
            'details':'Catalog linked tomb_alpha (user_17) to user_17.'}])
        index=EvidenceIndex.__new__(EvidenceIndex); index.facts=[]
        index.media={'screen_alpha':'Customer Reference Registry\nuser 17\nRetained reference'}
        index.link_documents(c)
        self.assertEqual(index.facts[0].resource,'tomb_alpha'); self.assertEqual(index.facts[0].state,'REDACTED')
        index.facts=[]; index.media={'screen_alpha':'Customer Reference Registry user 170'}
        index.link_documents(c)
        self.assertEqual(index.facts,[])

    def test_targeted_source_reread_repairs_missing_token_index(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as directory:
            directory=Path(directory)
            data={'exported_at':EARLY.isoformat(),'records':[
                {'recorded_at':EARLY.isoformat(),'system':'account_service','resource_id':'profile_alpha',
                 'record_type':'USER_PROFILE','result':'NOT_FOUND','subject_reference':'subject_alpha'},
                {'recorded_at':EARLY.isoformat(),'system':'security_service','resource_id':'journal_alpha',
                 'record_type':'SECURITY_AUDIT_LOG','result':'FOUND','subject_reference':'subject_alpha'}]}
            path=directory/'records.json'; path.write_text(json.dumps(data))
            source={'file_id':'records_alpha','file_path':'records.json','captured_at':EARLY.isoformat()}
            corpus=SimpleNamespace(root=directory,manifest=[source],activities=[],identities=[IDENTITY],history=[],rules=RULES,
                sources={'records_alpha':EARLY})
            index=EvidenceIndex(corpus)
            for token,items in list(index.by_token.items()):
                index.by_token[token]=[f for f in items if f.category!='USER_PROFILE']
            engine=Engine(corpus,index); draft=engine.investigate(CASE)
            guard=GhostGuard(corpus,index)
            self.assertTrue(guard.review(draft,engine.policy,{'subject_alpha','alex@example.test'}))
            repaired,new_index,sources=engine.reinvestigate(CASE,draft)
            guard.refresh(new_index)
            self.assertEqual(sources,['records_alpha'])
            self.assertEqual(guard.review(repaired,engine.policy,{'subject_alpha','alex@example.test'}),[])
            self.assertIn('profile_alpha',[f.resource for f in repaired.facts])

    def test_unknown_archive_has_no_fabricated_risk(self):
        c,i=fake_environment([fact('archive_alpha','backup_service','BACKUP_ARCHIVE','UNKNOWN')])
        with self.assertRaisesRegex(ValueError,'Unresolved state'): Engine(c,i).investigate(CASE)

    def test_targeted_reread_rejects_source_mutation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as directory:
            directory=Path(directory); path=directory/'records.json'; path.write_text('{}')
            f=replace(fact(),source='mutable_source')
            c,i=fake_environment([f]); c.root=directory
            c.manifest=[{'file_id':'mutable_source','file_path':'records.json','captured_at':EARLY.isoformat()}]
            i.source_hashes={'mutable_source':hashlib.sha256(path.read_bytes()).hexdigest()}
            engine=Engine(c,i); draft=engine.investigate(CASE)
            path.write_text('{"modified":true}')
            with self.assertRaisesRegex(ValueError,'Source changed'): engine.reinvestigate(CASE,draft)


class IntentRecoveryTests(unittest.TestCase):
    def test_negated_requests_in_multiple_languages(self):
        for text in ["I do not want to delete my account.","Please don't delete or change anything on my account.",
                     'アカウントを削除しないでください。','不要删除我的账户。',
                     'No quiero eliminar mi cuenta.','Ne supprimez pas mon compte.',
                     'Não quero excluir minha conta.','Bitte löschen Sie mein Konto nicht.']:
            with self.subTest(text=text): self.assertFalse(deletion_intent(text))

    def test_retention_exception_does_not_negate_account_deletion(self):
        self.assertTrue(deletion_intent('Please delete my account, but do not delete legally retained invoices.'))

    def test_policy_question_is_not_authorization(self):
        self.assertFalse(deletion_intent('Please explain the deletion policy for my account.'))

    def test_explicit_disposal_of_personal_profile_is_deletion(self):
        self.assertTrue(deletion_intent('I withdraw my consent to retain my personal profile; please dispose of it.'))


class TemporalAndSourceSafetyTests(unittest.TestCase):
    def test_new_primary_absence_does_not_clear_older_replica_presence(self):
        replica=fact(scope='customer_data_read_replica')
        primary=replace(fact(state='ABSENT',scope='customer_data_primary'),observed=CUTOFF,captured=CUTOFF)
        c,i=fake_environment([replica,primary]); result=Engine(c,i).investigate(CASE)
        self.assertEqual(result.status,'INCOMPLETE')
        self.assertTrue(any('Conflicting replica scope' in item for item in result.issues))

    def test_new_absence_on_same_replica_supersedes_old_presence(self):
        old=fact(scope='customer_data_read_replica')
        new=replace(old,state='ABSENT',observed=CUTOFF,captured=CUTOFF)
        c,i=fake_environment([old,new]); self.assertEqual(Engine(c,i).investigate(CASE).status,'COMPLETE')

    def test_archive_listing_does_not_change_known_restore_permission(self):
        old=fact('archive_alpha','backup_service','BACKUP_ARCHIVE','BLOCKED')
        listing=replace(old,state='UNKNOWN',observed=CUTOFF,captured=CUTOFF)
        c,i=fake_environment([old,listing]); result=Engine(c,i).investigate(CASE)
        self.assertEqual(result.facts[0].state,'BLOCKED')

    def test_restore_access_check_cannot_support_forged_blocked_state(self):
        f=fact('archive_alpha','backup_service','BACKUP_ARCHIVE','ACTIVE',source='check_alpha')
        c,i=fake_environment([f]); c.activities=[{'activity_id':'check_alpha','event_time':EARLY.isoformat(),
            'event_type':'CHECK_RESTORE_ACCESS','target_system':'backup_service','source_system':'worker',
            'resource_id':'archive_alpha','reported_result':'SUCCESS','details':'Archive archive_alpha can still be restored.'}]
        guard=GhostGuard(c,i)
        self.assertTrue(guard.source_supports(f))
        self.assertFalse(guard.source_supports(replace(f,state='BLOCKED')))

    def test_untrusted_step_shape_fails_with_value_error(self):
        from ghosttrace.models import Audit
        from ghosttrace.validator import validate_audit
        for steps in [[1],[None],[{'phase':'invented'}],False]:
            with self.subTest(steps=steps),self.assertRaises(ValueError):
                validate_audit(Audit(CASE,'',[],'COMPLETE',steps),{})

    def test_extra_schema_valid_operation_is_rejected_semantically(self):
        from ghosttrace.models import Audit
        from ghosttrace.policy import Policy
        from ghosttrace.compiler import compile_steps,make_step,sort_key
        f=fact(); policy=Policy(RULES); status,steps=compile_steps([f],policy,CUTOFF)
        steps.append(make_step('REMEDIATION','BLOCK_RESTORE',f))
        steps.sort(key=sort_key)
        for n,s in enumerate(steps,1): s['step_no']=n
        c,i=fake_environment([f]); guard=GhostGuard(c,i)
        with patch.object(guard,'source_supports',return_value=True):
            issues=guard.review(Audit(CASE,'subject_alpha',[f],status,steps),policy,{'alex@example.test'})
        self.assertTrue(any('Unsupported policy operation/state' in issue for issue in issues))

    def test_missing_tombstone_reference_not_verified_as_successful_redaction(self):
        c,i=fake_environment([fact('tomb_alpha','identity_service','ACCOUNT_TOMBSTONE','ABSENT')])
        with self.assertRaisesRegex(ValueError,'retained context/reference'): Engine(c,i).investigate(CASE)


class BoundedAIContractTests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{'OPENAI_API_KEY':'fixture-key-not-real'},clear=True); self.env.start()
        self.config=AIConfig(model='fixture-model',input_usd_per_m=1,output_usd_per_m=2)
    def tearDown(self): self.env.stop()

    def response(self,text,intent='DELETION'):
        return {'model':'fixture-model-snapshot','status':'completed','usage':{'input_tokens':10,'output_tokens':5},
            'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({'intent':intent,'quote':text})}]}]}

    def test_live_call_is_not_made_without_configured_model(self):
        calls=[]; client=IntentAI(AIConfig(),transport=lambda *a:calls.append(a))
        self.assertIsNone(client.classify('An ambiguous request')); self.assertEqual(calls,[])

    def test_structured_request_and_actual_response_usage(self):
        text='Erase the profile.'; payloads=[]
        def transport(payload,key,timeout): payloads.append(json.loads(payload)); return self.response(text)
        client=IntentAI(self.config,transport=transport)
        self.assertTrue(client.classify(text)); self.assertEqual(client.usage['input_tokens'],10)
        self.assertEqual(client.usage['output_tokens'],5)
        self.assertAlmostEqual(client.usage['estimated_cost_usd'],.00002)
        self.assertIn('fixture-model-snapshot',client.usage['models'])
        self.assertTrue(payloads[0]['text']['format']['strict']); self.assertFalse(payloads[0]['store'])

    def test_invented_quote_rejected(self):
        client=IntentAI(self.config,transport=lambda *a:self.response('Invented source content'))
        self.assertIsNone(client.classify('An ambiguous request'))

    def test_extra_model_ids_or_actions_rejected(self):
        with self.assertRaises(ValueError): IntentAI.validate({'intent':'DELETION','quote':'erase','resource_id':'invented'},'erase')

    def test_invalid_enum_rejected(self):
        with self.assertRaises(ValueError): IntentAI.validate({'intent':'COMPLETE','quote':'erase'},'erase')

    def test_authentication_failure_circuit_breaks_without_retry(self):
        calls=[]
        def transport(*args): calls.append(True); raise urllib.error.HTTPError('',401,'unauthorized',{},None)
        client=IntentAI(self.config,transport=transport)
        self.assertIsNone(client.classify('An ambiguous request'))
        self.assertIsNone(client.classify('A second ambiguous request'))
        self.assertEqual(len(calls),1); self.assertEqual(client.disabled_reason,'HTTP 401')
        self.assertFalse(client.usage['usage_complete'])

    def test_transient_retry_is_bounded(self):
        calls=[]
        def transport(*args): calls.append(True); raise urllib.error.HTTPError('',503,'unavailable',{},None)
        client=IntentAI(self.config,transport=transport)
        with patch('ghosttrace.ai.time.sleep'): self.assertIsNone(client.classify('An ambiguous request'))
        self.assertEqual(len(calls),2)

    def test_budget_checked_before_provider_request(self):
        calls=[]; client=IntentAI(replace(self.config,max_cost_usd=0),transport=lambda *a:calls.append(True))
        self.assertIsNone(client.classify('An ambiguous request')); self.assertEqual(calls,[])

    def test_call_limit_checked_before_provider_request(self):
        client=IntentAI(replace(self.config,max_calls=0),transport=lambda *a:self.fail('Provider request exceeds limit'))
        self.assertIsNone(client.classify('An ambiguous request'))

    def test_cache_invalidates_by_text_and_model(self):
        calls=[]
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as directory:
            def transport(payload,*args):
                text=json.loads(json.loads(payload)['input'])['request_text']; calls.append(text); return self.response(text)
            client=IntentAI(self.config,cache_dir=directory,transport=transport)
            self.assertTrue(client.classify('Erase alpha')); self.assertTrue(client.classify('Erase alpha'))
            self.assertEqual(len(calls),1); self.assertEqual(client.usage['cache_hits'],1)
            self.assertTrue(client.classify('Erase beta')); self.assertEqual(len(calls),2)
            other=IntentAI(replace(self.config,model='second-fixture-model'),cache_dir=directory,transport=transport)
            other.classify('Erase alpha'); self.assertEqual(len(calls),3)

    def test_incomplete_response_does_not_make_decision(self):
        response=self.response('Erase alpha'); response['status']='incomplete'
        client=IntentAI(self.config,transport=lambda *a:response)
        self.assertIsNone(client.classify('Erase alpha')); self.assertEqual(client.usage['successful_calls'],1)

    def test_unknown_usage_is_not_reported_as_measured_zero(self):
        response=self.response('Erase alpha'); response.pop('usage')
        client=IntentAI(self.config,transport=lambda *a:response)
        self.assertIsNone(client.classify('Erase alpha')); self.assertFalse(client.usage['usage_complete'])

    def test_malformed_provider_body_falls_back(self):
        self.assertIsNone(IntentAI(self.config,transport=lambda *a:[]).classify('Ambiguous request'))

    def test_large_request_not_sent(self):
        client=IntentAI(self.config,transport=lambda *a:self.fail('Oversized input was sent'))
        self.assertIsNone(client.classify('a'*3001))

    def test_uncertain_answer_does_not_authorize_deletion(self):
        client=IntentAI(self.config,transport=lambda *a:self.response('Maybe close it','UNCERTAIN'))
        self.assertIsNone(client.classify('Maybe close it'))


if __name__=='__main__': unittest.main()
