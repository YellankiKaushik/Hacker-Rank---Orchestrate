"""Contract-derived review distinctions and honest complete prediction coverage."""
import copy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_core import ROOT,EARLY,CUTOFF,LATE,CASE,IDENTITY,RULES,fact,fake_environment
from ghosttrace.models import Audit
from ghosttrace.engine import Engine
from ghosttrace.compiler import compile_steps,write_output
from ghosttrace.policy import Policy
from ghosttrace.reviewer import GhostGuard
from ghosttrace.validator import validate_audit
from ghosttrace.candidate import validate_candidate_audit,validate_candidate_file,validate_emitted_sources,uncertainty
from ghosttrace.ai import AIConfig,IntentAI,ollama_transport


class ObligationReviewTests(unittest.TestCase):
    def review(self,facts):
        c,i=fake_environment(facts); e=Engine(c,i); a=e.investigate(CASE); g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=True): issues=g.review(a,e.policy,{'alex@example.test'})
        return a,g,e,issues

    def test_a_profile_absence_is_sufficient_with_all_known_obligations(self):
        a,g,e,issues=self.review([fact(state='ABSENT')])
        self.assertEqual(issues,[]); self.assertEqual(a.coverage_proofs[0]['classification'],'A')

    def test_b_secondary_treatment_does_not_require_unrelated_profile(self):
        a,g,e,issues=self.review([fact('secondary','search_service','SEARCH_INDEX_ENTRY','ABSENT')])
        self.assertEqual(issues,[]); self.assertEqual(a.coverage_proofs[0]['classification'],'B')

    def test_c_retention_alone_does_not_establish_deletion(self):
        a,g,e,issues=self.review([fact('journal','security_service','SECURITY_AUDIT_LOG','PRESENT')])
        self.assertTrue(issues); self.assertEqual(a.coverage_proofs[0]['classification'],'C')

    def test_c_unbound_root_in_same_source_is_not_silently_ignored(self):
        treated=fact('secondary','search_service','SEARCH_INDEX_ENTRY','ABSENT')
        orphan=replace(fact('unassigned',state='ABSENT'),data={})
        a,g,e,issues=self.review([treated,orphan])
        self.assertTrue(any('unbound account' in v for v in issues))

    def test_other_subject_root_does_not_create_our_obligation(self):
        treated=fact('secondary','search_service','SEARCH_INDEX_ENTRY','ABSENT')
        other=replace(fact('other'),data={'subject_reference':'subject_beta'})
        c,i=fake_environment([treated,other]); c.identities.append({**IDENTITY,'user_id':'subject_beta','email':'beta@example.test'})
        a=Engine(c,i).investigate(CASE); g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=True): self.assertEqual(g.review(a,Policy(RULES),{'alex@example.test'}),[])

    def test_d_complete_cannot_hide_known_present_profile(self):
        c,i=fake_environment([fact()]); e=Engine(c,i); a=e.investigate(CASE); a.status='COMPLETE'
        a.steps=[{'step_no':1,'phase':'VERIFICATION','system_id':'account_service','resource_id':'profile_alpha',
                  'operation':'VERIFY_RECORD_ABSENT','state':'ABSENT','evidence_id':'source_alpha'}]
        g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=True): issues=g.review(a,e.policy,{'alex@example.test'})
        self.assertTrue(any('Contradicted COMPLETE' in v for v in issues)); self.assertEqual(a.coverage_proofs[0]['classification'],'D')

    def test_e_source_fabrication_is_blocking(self):
        c,i=fake_environment([fact(state='ABSENT')]); e=Engine(c,i); a=e.investigate(CASE); g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=False): issues=g.review(a,e.policy,{'alex@example.test'})
        self.assertTrue(issues); self.assertEqual(a.coverage_proofs[0]['classification'],'E')

    def test_reviewer_cannot_mislabel_deletion_as_not_applicable(self):
        c,i=fake_environment([fact()]); g=GhostGuard(c,i)
        self.assertTrue(g.review(Audit(CASE,'',[],'NOT_APPLICABLE',[]),Policy(RULES),set()))

    def test_reviewer_rejects_non_deletion_with_deletion_plan(self):
        c,i=fake_environment([fact()]); a=Engine(c,i).investigate(CASE)
        a.case={**CASE,'request_text':'Please send me a copy of my account information.'}
        self.assertTrue(GhostGuard(c,i).review(a,Policy(RULES),{'alex@example.test'}))

    def test_known_linked_missing_state_blocks_secondary_only_complete(self):
        treated=fact('secondary','search_service','SEARCH_INDEX_ENTRY','ABSENT')
        c,i=fake_environment([treated]); c.activities=[{'event_type':'LINK_RESOURCE_IDENTITY','event_time':EARLY.isoformat(),
            'activity_id':'catalog','target_system':'account_service','resource_id':'unobserved','details':'alex@example.test'}]
        a=Engine(c,i).investigate(CASE); g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=True): issues=g.review(a,Policy(RULES),{'alex@example.test'})
        self.assertTrue(any('Missing bound' in v for v in issues))

    def test_source_reread_rejects_forged_owner_on_a_real_resource_state(self):
        import hashlib
        from types import SimpleNamespace
        from ghosttrace.adapters import EvidenceIndex
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            root=Path(d); path=root/'source.log'
            path.write_text('2026-01-01T00:00:00Z service=account_service event=profile_lookup_completed resource_id=profile_alpha rows=0 lookup_key=other@example.test\n')
            c=SimpleNamespace(root=root,manifest=[{'file_id':'real','file_path':'source.log','captured_at':EARLY.isoformat()}],activities=[])
            i=EvidenceIndex(c); g=GhostGuard(SimpleNamespace(**vars(c),identities=[IDENTITY]),i)
            real=i.facts[0]; forged=replace(real,data={**real.data,'lookup_key':'alex@example.test'})
            self.assertTrue(g.source_supports(real)); self.assertFalse(g.source_supports(forged))


class CandidateSafetyTests(unittest.TestCase):
    def test_unknown_restore_has_no_fabricated_risk_or_blocked_verification(self):
        c,i=fake_environment([fact('archive','backup_service','BACKUP_ARCHIVE','UNKNOWN')]); e=Engine(c,i)
        with self.assertRaises(ValueError): e.investigate(CASE)
        a=e.investigate(CASE,permit_partial=True)
        self.assertEqual(a.status,'INCOMPLETE'); self.assertEqual(a.steps,[])
        validate_candidate_audit(a,c.sources)
        with self.assertRaises(ValueError): validate_audit(a,c.sources)

    def test_unverified_complete_is_explicitly_counted(self):
        c,i=fake_environment([fact('journal','security_service','SECURITY_AUDIT_LOG','PRESENT')]); e=Engine(c,i)
        a=e.investigate(CASE,permit_partial=True); g=GhostGuard(c,i)
        issue=uncertainty(CASE,a,'No deletion coverage',g,e.policy,{'alex@example.test'})
        self.assertEqual(issue['unsupported_status_inferences'],1)
        self.assertIn('not proven',issue['status_inference'])

    def test_unknown_permission_does_not_override_established_other_violation(self):
        c,i=fake_environment([fact(),fact('archive','backup_service','BACKUP_ARCHIVE','UNKNOWN')]); e=Engine(c,i)
        a=e.investigate(CASE,permit_partial=True)
        self.assertEqual(a.status,'INCOMPLETE')
        self.assertEqual({s['resource_id'] for s in a.steps},{'profile_alpha'})

    def test_non_deletion_never_filled_as_deletion(self):
        case={**CASE,'request_text':'Please send me a copy of my account information.'}
        with self.assertRaises(ValueError): validate_candidate_audit(Audit(case,'',[],'COMPLETE',[]),{})
        validate_candidate_audit(Audit(case,'',[],'NOT_APPLICABLE',[]),{})

    def test_deletion_never_filled_as_non_deletion(self):
        with self.assertRaises(ValueError): validate_candidate_audit(Audit(CASE,'',[],'NOT_APPLICABLE',[]),{})

    def test_fabricated_source_reference_cannot_fill_candidate(self):
        c,i=fake_environment([fact()]); e=Engine(c,i); a=e.investigate(CASE); a.steps[0]['evidence_id']='fabricated'
        with self.assertRaises(ValueError): validate_candidate_audit(a,c.sources)

    def test_wrong_real_citation_cannot_fill_candidate(self):
        c,i=fake_environment([fact()]); e=Engine(c,i); a=e.investigate(CASE); a.steps[0]['evidence_id']='other_real'
        g=GhostGuard(c,i)
        with patch.object(g,'source_supports',return_value=True):
            with self.assertRaisesRegex(ValueError,'citation does not prove'): validate_emitted_sources(a,g,e.policy,{'alex@example.test'})

    def test_future_citation_cannot_fill_candidate(self):
        c,i=fake_environment([fact()]); a=Engine(c,i).investigate(CASE)
        with self.assertRaises(ValueError): validate_candidate_audit(a,{'source_alpha':LATE})

    def test_invented_resource_without_bound_fact_rejected(self):
        c,i=fake_environment([fact()]); e=Engine(c,i); a=e.investigate(CASE); a.steps[0]['resource_id']='fabricated'
        with self.assertRaises(ValueError): validate_emitted_sources(a,GhostGuard(c,i),e.policy,{'alex@example.test'})

    def test_candidate_roundtrip_count_and_atomic_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp/tests') as d:
            path=Path(d)/'candidate.csv'; path.write_text('previous')
            bad=Audit(CASE,'',[],'NOT_APPLICABLE',[])
            with self.assertRaises(ValueError):
                write_output(path,[bad],lambda p:validate_candidate_file(p,[CASE],{}))
            self.assertEqual(path.read_text(),'previous')

    def test_unknown_state_is_not_cited_as_current_compliance(self):
        unknown=fact('archive','backup_service','BACKUP_ARCHIVE','UNKNOWN')
        c,i=fake_environment([unknown]); e=Engine(c,i); a=e.investigate(CASE,permit_partial=True)
        a.steps=[{'step_no':1,'phase':'VERIFICATION','system_id':'backup_service','resource_id':'archive',
                  'operation':'VERIFY_RESTORE_BLOCKED','state':'BLOCKED','evidence_id':'source_alpha'}]
        with self.assertRaises(ValueError): validate_emitted_sources(a,GhostGuard(c,i),e.policy,{'alex@example.test'})


class LocalAIContractTests(unittest.TestCase):
    def test_local_configuration_does_not_require_cloud_key_or_invent_price(self):
        with patch.dict('os.environ',{},clear=True):
            client=IntentAI(AIConfig(provider='ollama',model='fixture-local'))
            self.assertTrue(client.ready()); self.assertEqual(client.config.input_usd_per_m,0)

    def test_unknown_provider_rejected(self):
        with self.assertRaises(ValueError): AIConfig(provider='invented')

    def test_local_transport_uses_fixed_loopback_and_no_authorization(self):
        from unittest.mock import MagicMock
        response=MagicMock(); response.__enter__.return_value.read.return_value=json.dumps({
            'model':'fixture-local','done':True,'done_reason':'stop','prompt_eval_count':17,'eval_count':9,
            'message':{'content':'{"intent":"UNCERTAIN","quote":"maybe"}'}}).encode()
        opener=MagicMock(); opener.open.return_value=response
        payload=json.dumps({'model':'fixture-local','instructions':'classify','input':'maybe','max_output_tokens':128}).encode()
        with patch('urllib.request.build_opener',return_value=opener): result=ollama_transport(payload,'must-not-leak',10)
        request=opener.open.call_args.args[0]
        self.assertEqual(request.full_url,'http://127.0.0.1:11434/api/chat')
        self.assertNotIn('Authorization',request.headers)
        self.assertEqual(result['usage'],{'input_tokens':17,'output_tokens':9})


if __name__=='__main__': unittest.main()
