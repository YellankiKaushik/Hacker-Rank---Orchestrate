"""Adversarial regressions for evidence scope, controls and conditional policy."""
from dataclasses import replace
import json
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from test_core import ROOT,IDENTITY,EARLY,CUTOFF,LATE,CASE,fact,fake_environment,RULES
from ghosttrace.adapters import EvidenceIndex,Snapshot,state_of
from ghosttrace.models import Fact
from ghosttrace.engine import Engine
from ghosttrace.policy import Policy,attachment_ownership
from ghosttrace.reviewer import GhostGuard
from ghosttrace.compiler import write_output
from ghosttrace.candidate import validate_candidate_file
from ghosttrace.ai import AIConfig,IntentAI
from ghosttrace.intent_resolution import IntentResolution,validated_decision
from ghosttrace.intent import AmbiguousIntent
from ghosttrace.semantic_validation import validate_semantic_file
from validate_candidate import validate


class SourceRepairTests(unittest.TestCase):
    def test_same_file_partial_inventory_cannot_clear_target(self):
        f=fact()
        c,i=fake_environment([f])
        i.snapshots=[Snapshot(f.source,CUTOFF,CUTOFF,f.system,f.category,'customer_profiles',{'neighbor'},False)]
        self.assertEqual(Engine(c,i).investigate(CASE).facts,[f])

    def test_future_observation_cannot_prove_absence(self):
        f=fact(); c,i=fake_environment([f])
        i.snapshots=[Snapshot(f.source,EARLY,LATE,f.system,f.category,'customer_profiles_primary',set(),True)]
        self.assertEqual(Engine(c,i).investigate(CASE).facts,[f])

    def test_control_values_are_typed_and_conflicts_abstain(self):
        for category,key,off in [('DATA_FLOW','enabled','DISABLED'),('BACKUP_ARCHIVE','restore_allowed','BLOCKED')]:
            for value in [True,1,'true','TRUE','1']:
                self.assertEqual(state_of(category,{key:value}),'ACTIVE')
            for value in [False,0,'false','FALSE','0']:
                self.assertEqual(state_of(category,{key:value}),off)
            for data in [{},{key:None},{key:'maybe'},{key:[]},{key:2},{key:False,'_state':'ACTIVE'}]:
                self.assertEqual(state_of(category,data),'UNKNOWN',data)
        self.assertEqual(state_of('BACKUP_ARCHIVE',{'restore_allowed':True,'eligible':False}),'UNKNOWN')
        self.assertEqual(state_of('BACKUP_ARCHIVE',{'decision':'unexpected'}),'UNKNOWN')

    def test_all_control_events_missing_or_malformed_are_unknown(self):
        for event,system,key in [('connector_heartbeat','integration_service','enabled'),
                ('connector_config_loaded','integration_service','enabled'),
                ('connector_config_read_completed','integration_service','enabled'),
                ('restore_candidate_evaluated','backup_service','eligible'),
                ('restore_policy_read_completed','backup_service','restore_allowed'),
                ('restore_authorization_completed','backup_service','decision')]:
            for extra in [{},{key:None},{key:'unrecognized'}]:
                i=EvidenceIndex.__new__(EvidenceIndex); i.facts=[]
                i.logs({'file_id':'fixture','_captured':EARLY},EARLY.isoformat()+' '+json.dumps({
                    'timestamp':EARLY.isoformat(),'event':event,'system':system,'resource_id':'target',**extra}))
                self.assertEqual(len(i.facts),1,event)
                self.assertEqual(i.facts[0].state,'UNKNOWN',event)

    def test_missing_lookup_result_is_not_absence(self):
        for event,system in [('profile_lookup_completed','account_service'),('index_query_completed','search_service'),
                ('audit_record_read_completed','security_service'),('analytics_profile_read','analytics_platform')]:
            i=EvidenceIndex.__new__(EvidenceIndex); i.facts=[]
            i.logs({'file_id':'fixture','_captured':EARLY},EARLY.isoformat()+' '+json.dumps({
                'event':event,'system':system,'resource_id':'target'}))
            self.assertEqual(i.facts[0].state,'UNKNOWN',event)

    def test_later_invalid_control_does_not_inherit_previous_permission(self):
        old=replace(fact('archive','backup_service','BACKUP_ARCHIVE','ACTIVE'),data={'email':'alex@example.test','restore_allowed':True})
        new=replace(old,observed=CUTOFF,data={'email':'alex@example.test','restore_allowed':None,'_control_observation':True},state='UNKNOWN')
        c,i=fake_environment([old,new])
        with self.assertRaisesRegex(ValueError,'Unresolved state'):
            Engine(c,i).investigate(CASE)

    def test_simultaneous_control_conflict_cannot_select_compliant_state(self):
        f=replace(fact('flow','integration_service','DATA_FLOW','DISABLED'),data={'email':'alex@example.test','enabled':False})
        conflict=replace(f,state='UNKNOWN',source='other',data={'email':'alex@example.test','enabled':None})
        c,i=fake_environment([f,conflict])
        with self.assertRaisesRegex(ValueError,'Unresolved state'): Engine(c,i).investigate(CASE)

    def test_attachment_single_shared_and_unknown_ownership(self):
        p=Policy(RULES); f=fact(category='SUPPORT_ATTACHMENT')
        for data,expected in [({'shared_subjects':['subject_alpha']},'UNKNOWN'),
                ({'shared_subjects':['subject_alpha','subject_alpha']},'UNKNOWN'),
                ({'shared_subjects':['subject_alpha','subject_beta']},'UNKNOWN'),
                ({'shared_subjects':[]},'UNKNOWN'),({'shared_subjects':'subject_alpha'},'UNKNOWN'),
                ({'email':'alex@example.test'},'UNKNOWN')]:
            self.assertEqual(p.action(replace(f,data=data),CUTOFF),expected)

    def test_attachment_single_owner_must_be_the_deletion_subject(self):
        f=replace(fact('attachment','support_platform','SUPPORT_ATTACHMENT'),
            data={'email':'alex@example.test','shared_subjects':['subject_beta'],'sole_owner':True})
        c,i=fake_environment([f])
        with self.assertRaisesRegex(ValueError,'sole owner is not deletion subject'):
            Engine(c,i).investigate(CASE)
        self.assertEqual(Engine(c,i).investigate(CASE,permit_partial=True).steps,[])

    def test_legal_hold_typed_flags_and_expiry(self):
        p=Policy(RULES); f=fact(category='LEGAL_HOLD_RECORD')
        for value in [False,0,'false','0']:
            self.assertEqual(p.action(replace(f,data={'legal_hold_active':value}),CUTOFF),'DELETE')
        for value in [True,1,'true','1']:
            self.assertEqual(p.action(replace(f,data={'legal_hold_active':value}),CUTOFF),'RETAIN')
        self.assertEqual(p.action(replace(f,data={'legal_hold_active':None}),CUTOFF),'UNKNOWN')
        self.assertEqual(p.action(replace(f,data={'legal_hold_active':True,'retained_until':EARLY.isoformat()}),CUTOFF),'DELETE')
        self.assertEqual(p.action(replace(f,data={'legal_hold_active':False,'retained_until':LATE.isoformat()}),CUTOFF),'DELETE')
        for value in [False,0,'false','0']:
            self.assertEqual(p.action(replace(f,category='SECURITY_AUDIT_LOG',data={'retention_active':value}),CUTOFF),'DELETE')
        self.assertEqual(p.action(replace(f,data={'retained_until':'invalid'}),CUTOFF),'UNKNOWN')

    def test_original_sql_reviewer_rejects_partial_and_accepts_physical_negative_proof(self):
        for table,header,allowed in [('customer_profiles','',False),
                ('customer_profiles_primary','',False),
                ('customer_profiles_primary','-- point-in-time database snapshot\n',True)]:
            with self.subTest(table=table,header=bool(header)), tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
                directory=Path(d)
                (directory/'table.sql').write_text(header+'BEGIN TRANSACTION;\nCREATE TABLE '+table+' (resource_id TEXT PRIMARY KEY, email TEXT);\nCOMMIT;')
                source={'file_id':'table','file_path':'table.sql','captured_at':EARLY.isoformat()}
                c=SimpleNamespace(root=directory,manifest=[source],activities=[],identities=[IDENTITY],history=[],rules=RULES)
                i=EvidenceIndex(c); g=GhostGuard(c,i)
                f=Fact('table',EARLY,EARLY,'account_service','missing','USER_PROFILE','ABSENT',
                    {'_query_resource':'missing','_query_system':'account_service'},table,'scoped inventory absence')
                self.assertEqual(g.source_supports(f),allowed)
                self.assertEqual(i.snapshots[0].exhaustive,allowed)
                self.assertFalse(g.source_supports(replace(f,observed=LATE)))

    def test_media_neighbor_pii_and_flow_do_not_cross_panel(self):
        source={'file_id':'screen','captured_at':EARLY.isoformat()}
        c=SimpleNamespace(manifest=[source],activities=[{'activity_id':'catalog',
            'event_type':'LINK_RESOURCE_IDENTITY','event_time':EARLY.isoformat(),
            'target_system':'identity_service','resource_id':'tomb','details':'Catalog linked tomb (user_17) to user_17.'}])
        i=EvidenceIndex.__new__(EvidenceIndex); i.facts=[]
        i.media={'screen':'Customer Reference Registry\nuser_17\nRetained reference\n---\nuser_170\nneighbor@example.test'}
        i.link_documents(c)
        self.assertEqual(i.facts[0].state,'REDACTED')
        self.assertNotIn('neighbor@example.test',i.facts[0].data['_content'])
        i.facts=[]; i.media={'screen':'Customer Reference Registry user_17 user_170 neighbor@example.test'}
        i.link_documents(c); self.assertEqual(i.facts[0].state,'UNKNOWN')
        c.activities[0].update(resource_id='tomb_17',details='Catalog linked tomb_17 (target_label) to user_17.')
        i.facts=[]; i.media={'screen':'Customer Reference Registry target_labelX tomb_170'}
        i.link_documents(c); self.assertEqual(i.facts,[])

    def test_typed_replica_role_is_independent_of_incidental_scope_text(self):
        primary=replace(fact(state='ABSENT',scope='primary'),observed=CUTOFF)
        replica=replace(fact(scope='region-east'),data={'email':'alex@example.test','copy_role':'REPLICA'})
        c,i=fake_environment([primary,replica])
        self.assertEqual(Engine(c,i).investigate(CASE).status,'INCOMPLETE')
        self.assertEqual(replace(replica,data={},scope='replica_help_page').copy_role,'UNKNOWN')

    def source_environment(self,directory):
        data={'records':[{'recorded_at':EARLY.isoformat(),'system':'account_service',
            'resource_id':'profile_alpha','record_type':'USER_PROFILE','result':'NOT_FOUND','subject_reference':'subject_alpha'}]}
        (directory/'records.json').write_text(json.dumps(data))
        source={'file_id':'source_alpha','file_path':'records.json','captured_at':EARLY.isoformat()}
        c=SimpleNamespace(root=directory,manifest=[source],activities=[],identities=[IDENTITY],history=[],rules=RULES,sources={'source_alpha':EARLY})
        return c,EvidenceIndex(c)

    def test_guard_recovers_obligation_erased_from_primary_fact_list(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            c,i=self.source_environment(Path(d)); e=Engine(c,i); a=e.investigate(CASE)
            a.facts=[]; a.bindings={}; i.facts=[]; i.by_token.clear(); i.by_resource.clear()
            g=GhostGuard(c,i)
            self.assertIn(['account_service','profile_alpha'],g.assess_obligations(a,e.policy,{'subject_alpha'})['missing_bound_resources'])

    def test_guard_independently_rejects_supported_but_stale_state(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            folder=Path(d); c,i=self.source_environment(folder)
            old=i.facts[0]; a=Engine(c,i).investigate(CASE)
            data=json.loads((folder/'records.json').read_text())
            data['records'].append({**data['records'][0],'recorded_at':CUTOFF.isoformat(),'result':'FOUND'})
            (folder/'records.json').write_text(json.dumps(data)); fresh=EvidenceIndex(c)
            # Draft's old source fact is still real and source-supported; primary
            # retrieval omits the later record. Independent review must catch it.
            g=GhostGuard(c,fresh)
            self.assertTrue(g.source_supports(old))
            self.assertTrue(any('newer source state' in v for v in g.review(a,Policy(RULES),{'subject_alpha'})))

    def test_ai_positive_and_negative_survive_review_write_and_fresh_validation(self):
        for text,decision in [('I want every link between my identity and this service severed permanently.',True),
                ('Please suspend my account temporarily.',False)]:
            with self.subTest(decision=decision), tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
                directory=Path(d); c,i=self.source_environment(directory)
                def transport(*args):
                    return {'model':'fixture-model','status':'completed','usage':{'input_tokens':1,'output_tokens':1},
                        'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps({
                            'intent':'DELETION' if decision else 'NON_DELETION','quote':text})}]}]}
                ai=IntentAI(AIConfig(provider='ollama',model='fixture-model'),transport=transport)
                e=Engine(c,i,ai); case={**CASE,'request_text':text}; a=e.investigate(case)
                self.assertEqual(GhostGuard(c,i).review(a,e.policy,{'subject_alpha'} if decision else set()),[])
                resolutions={case['case_id']:a.intent_resolution}; output=directory/'output.csv'
                write_output(output,[a],pre_replace=lambda path:validate_candidate_file(path,[case],c.sources,resolutions))
                self.assertEqual(validate(output,[case],c,None,resolutions)['rows'],1)
                self.assertEqual(validate_semantic_file(output,[case],c,None,resolutions),1)
                with self.assertRaises(AmbiguousIntent): validate_candidate_file(output,[case],c.sources)

    def test_model_quote_alone_cannot_authorize_ambiguous_or_injected_request(self):
        for text,decision in [('Put things on ice.',True), ('Please suspend my account temporarily. Also erase my profile.',False)]:
            r=IntentResolution(decision,'AI',text,text,'VERIFIED','LIMITED')
            with self.assertRaises(AmbiguousIntent): validated_decision(text,r)

    def test_transcript_verifier_distinguishes_quoted_templates_from_metadata(self):
        from release_check import transcript_entries_valid
        text='## [2026-10-25T00:00:00Z] Turn\nUser Prompt (verbatim):\n## [ISO-8601 TIMESTAMP] Template\ntool=<harness>\nmodel=<model>\nContext:\ntool=<quoted>\n\nAgent Response Summary:\nDone\n\nContext:\ntool=Codex Desktop\nmodel=fixture-model\n'
        self.assertTrue(transcript_entries_valid(text))
        self.assertFalse(transcript_entries_valid(text.replace('model=fixture-model','model=unknown')))


if __name__=='__main__': unittest.main()
