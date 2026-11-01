"""Gemini e .env com credenciais fictícias; nenhum teste chama a API externa."""
from copy import deepcopy
from dataclasses import replace
from importlib.util import spec_from_file_location, module_from_spec, find_spec
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from managerai.config import backend_environment
from managerai.gemini_advisor import GeminiAdvisor, AdvisorFailure, projection_for, validate_advice
from managerai.service import build_service_report, render_service_markdown
from managerai.service_schema import ServiceRequest, ServiceError
from test_service import ServiceFixture

KEY = 'dummy-credential-for-tests'
REFS = ['team_profile.metrics.shots_for', 'opponent_profile.metrics.shots_for']


def valid_answer():
    return {'summary': 'Investigar o equilíbrio entre criação e proteção da área.', 'options': [{
        'title': 'Conferir a proteção da área', 'action': 'Considerar maior proteção das zonas de finalização.',
        'rationale': 'Comparar os chutes produzidos pelo adversário com os concedidos pela equipe.',
        'video_check': 'Observar como os adversários recebem na área.', 'adjust_when': 'Se as entradas adversárias persistirem.',
        'risks': ['Pode reduzir a presença ofensiva.'], 'evidence_ids': REFS.copy()}]}


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'.env'

    def test_file_process_precedence_quotes_unknown_keys_and_no_expansion(self):
        self.path.write_text('GEMINI_API_KEY="file-dummy" # comentário\nMANAGERAI_GEMINI_ENABLED=true\nVITE_SECRET=ignore\nMANAGERAI_DATA_ROOT=$(do-not-execute)\n')
        env = backend_environment(self.path, environ={'GEMINI_API_KEY': 'process-dummy'})
        self.assertEqual(env['GEMINI_API_KEY'], 'process-dummy')
        self.assertEqual(env['MANAGERAI_DATA_ROOT'], '$(do-not-execute)')
        self.assertNotIn('VITE_SECRET', env)
        self.assertEqual(backend_environment(self.path, environ={'GEMINI_API_KEY': ''})['GEMINI_API_KEY'], '')

    def test_bad_file_errors_never_include_values(self):
        for content in [f'GEMINI_API_KEY="{KEY}', f'GEMINI_API_KEY={KEY}\nGEMINI_API_KEY=again', 'MANAGERAI_GEMINI_ENABLED=maybe']:
            self.path.write_text(content)
            with self.assertRaises(ValueError) as error:
                backend_environment(self.path, environ={})
            self.assertNotIn(KEY, str(error.exception))
        with self.assertRaises(ValueError):
            backend_environment(self.path.parent/'missing', environ={'MANAGERAI_GEMINI_ENABLED': 'maybe'})

    def test_setup_creates_private_file_once_and_preserves_personal_key(self):
        script = Path(__file__).resolve().parents[1]/'scripts/setup_env.py'
        spec = spec_from_file_location('managerai_setup_env_test', script)
        module = module_from_spec(spec);spec.loader.exec_module(module)
        root = self.path.parent
        (root/'.env.example').write_text('GEMINI_API_KEY=\nMANAGERAI_GEMINI_ENABLED=false\n')
        self.assertTrue(module.create_local_env(root))
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        self.path.write_text(f'GEMINI_API_KEY={KEY}\n')
        self.assertFalse(module.create_local_env(root))
        self.assertEqual(self.path.read_text(), f'GEMINI_API_KEY={KEY}\n')


class GeminiTests(ServiceFixture):
    def report(self):
        return build_service_report(self.root, ServiceRequest(self.request))

    def test_projection_omits_notes_roster_sources_and_preserves_metric_samples(self):
        report = build_service_report(self.root, ServiceRequest(replace(self.request, notes='private-note')))
        p = projection_for(report)
        encoded=json.dumps(p)
        self.assertNotIn('private-note', encoded)
        self.assertNotIn('roster', p)
        self.assertNotIn('sources', p)
        self.assertTrue(all(m['sample_size'] >= 5 for m in p['evidence'].values()))
        for ref, metric in p['evidence'].items():
            self.assertEqual(metric['value'], report['evidence'][ref]['value'])

    def test_free_text_digits_unknown_ids_single_team_and_extra_fields_rejected(self):
        projection = projection_for(self.report())
        good = valid_answer()
        self.assertEqual(validate_advice(json.dumps(good), projection), good)
        bad = []
        for mutation in ('digits', 'unknown', 'one_side', 'extra', 'empty'):
            obj=deepcopy(good)
            if mutation=='digits': obj['summary']='Chance de vitória de 90%.'
            if mutation=='unknown': obj['options'][0]['evidence_ids']=['unknown']
            if mutation=='one_side': obj['options'][0]['evidence_ids']=[REFS[0]]
            if mutation=='extra': obj['options'][0]['players']=['Inventado']
            if mutation=='empty': obj['options']=[]
            bad.append(obj)
        for obj in bad:
            with self.subTest(obj=obj), self.assertRaises(AdvisorFailure):
                validate_advice(json.dumps(obj), projection)

    def test_transport_uses_header_fixed_endpoint_and_cache_without_retry(self):
        p=projection_for(self.report());reply={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(valid_answer())}]}}]}
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.read.return_value=json.dumps(reply).encode()
        opener=Mock();opener.open.return_value=response
        advisor=GeminiAdvisor(KEY)
        with patch('managerai.gemini_advisor.build_opener', return_value=opener):
            first,cached=advisor.generate(p);self.assertFalse(cached)
            second,cached=advisor.generate(p);self.assertTrue(cached)
            self.assertEqual(first, second);self.assertEqual(opener.open.call_count,1)
            request=opener.open.call_args.args[0]
            self.assertNotIn(KEY, request.full_url)
            self.assertEqual(request.get_header('X-goog-api-key'), KEY)
            self.assertNotIn(KEY, request.data.decode())
            changed=deepcopy(p);changed['context']['strategic_objective']='buscar gol'
            advisor.generate(changed);self.assertEqual(opener.open.call_count,2)

    def test_429_pauses_without_paid_fallback_or_response_leak(self):
        advisor=GeminiAdvisor(KEY);opener=Mock()
        opener.open.side_effect=HTTPError('https://example.invalid',429,KEY,None,None)
        with patch('managerai.gemini_advisor.build_opener',return_value=opener):
            for _ in range(2):
                with self.assertRaises(AdvisorFailure) as error: advisor.generate(projection_for(self.report()))
                self.assertEqual(str(error.exception),'RATE_LIMIT')
            self.assertEqual(opener.open.call_count,1)

    def test_truncation_and_unsafe_model_configuration_fail_closed(self):
        for model in ('https://example.invalid', '../../bad', 'gemini-model?key=anything'):
            with self.assertRaises(ValueError): GeminiAdvisor(KEY,model)
        advisor=GeminiAdvisor(KEY);response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.read.return_value=json.dumps({'candidates':[{'finishReason':'MAX_TOKENS','content':{'parts':[{'text':json.dumps(valid_answer())}]}}]}).encode()
        opener=Mock();opener.open.return_value=response
        with patch('managerai.gemini_advisor.build_opener',return_value=opener), self.assertRaises(AdvisorFailure):
            advisor.generate(projection_for(self.report()))

    def test_no_call_by_default_and_core_unchanged_with_generated_suggestions(self):
        advisor=Mock(provider_id='gemini',model='dummy');advisor.generate.return_value=(valid_answer(),False)
        plain=build_service_report(self.root,ServiceRequest(self.request),advisor=advisor)
        advisor.generate.assert_not_called()
        ai=build_service_report(self.root,ServiceRequest(self.request,ai_analysis='optional'),advisor=advisor)
        self.assertEqual(ai['ai_tactical']['status'],'generated')
        self.assertEqual(ai['legacy_report'],plain['legacy_report'])
        self.assertEqual(ai['evidence'],plain['evidence'])
        self.assertEqual(ai['plans'],plain['plans'])
        self.assertIn('Análise tática por IA',render_service_markdown(ai))

    def test_insufficiency_restrictions_and_unconfigured_advisor_preserve_report(self):
        advisor=Mock(provider_id='gemini',model='dummy')
        for req in (ServiceRequest(replace(self.request,recent_matches_window=1),ai_analysis='optional'),
                    ServiceRequest(self.request,blocked_plan_ids=('R03_CHANCES',),ai_analysis='optional')):
            report=build_service_report(self.root,req,advisor=advisor)
            self.assertEqual(report['ai_tactical']['status'],'abstained')
        advisor.generate.assert_not_called()
        report=build_service_report(self.root,ServiceRequest(self.request,ai_analysis='optional'))
        self.assertEqual(report['ai_tactical']['status'],'unavailable')
        self.assertTrue(report['evidence'])

    def test_invalid_injected_response_is_not_presented_as_success(self):
        advisor=Mock(provider_id='gemini',model='dummy');advisor.generate.return_value=({'text':KEY},False)
        report=build_service_report(self.root,ServiceRequest(self.request,ai_analysis='optional'),advisor=advisor)
        self.assertEqual(report['ai_tactical']['status'],'failed')
        self.assertNotIn(KEY,json.dumps(report))
        with self.assertRaises(ServiceError): ServiceRequest(self.request,ai_analysis='required')


@unittest.skipUnless(find_spec('fastapi') and find_spec('httpx'), 'API opcional')
class GeminiAPITests(ServiceFixture):
    def test_env_configuration_stays_in_backend_and_requests_default_to_none(self):
        from fastapi.testclient import TestClient
        from managerai.api import create_app
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'.env';path.write_text(f'GEMINI_API_KEY={KEY}\nMANAGERAI_GEMINI_ENABLED=true\n')
            with patch.dict(os.environ,{},clear=True): client=TestClient(create_app(data_root=self.root,env_file=path))
            caps=client.get('/v1/capabilities').json()
            self.assertTrue(caps['tactical_advisor']['configured'])
            self.assertNotIn(KEY,json.dumps(caps))
            body={'analysis':{'competition_id':2,'season_id':27,'team_id':1,'opponent_id':2,'target_match_id':8}}
            with patch('managerai.gemini_advisor.build_opener',side_effect=AssertionError('sem chamada externa')):
                response=client.post('/v1/analyses',json=body)
            self.assertEqual(response.status_code,200,response.text)
            self.assertNotIn('ai_tactical',response.json())
            self.assertNotIn(KEY,response.text)

    def test_generated_advice_survives_http_contract_and_exports_without_credentials(self):
        from fastapi.testclient import TestClient
        from managerai.api import create_app
        advisor=Mock(provider_id='gemini',model='test-model')
        advisor.generate.return_value=(valid_answer(),False)
        with tempfile.TemporaryDirectory() as temporary:
            client=TestClient(create_app(data_root=self.root,advisor=advisor,env_file=Path(temporary)/'missing'))
            body={'analysis':{'competition_id':2,'season_id':27,'team_id':1,'opponent_id':2,'target_match_id':8},'ai_analysis':'optional'}
            response=client.post('/v1/analyses',json=body)
            self.assertEqual(response.status_code,200,response.text)
            report=response.json()
            self.assertEqual(report['ai_tactical']['status'],'generated')
            self.assertEqual(client.get(f"/v1/reports/{report['report_key']}/export").json(),report)
            markdown=client.get(f"/v1/reports/{report['report_key']}/export?format=markdown")
            self.assertIn('Conferir a proteção da área',markdown.text)
            self.assertNotIn(KEY,response.text+markdown.text)
