"""Groq com chave fictícia; nenhuma geração externa é executada."""
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from importlib.util import find_spec

from managerai.config import backend_environment
from managerai.gemini_advisor import AdvisorFailure, projection_for
from managerai.groq_advisor import GroqAdvisor
from managerai.service import build_service_report
from managerai.service_schema import ServiceRequest
from test_service import ServiceFixture
from test_gemini import valid_answer

KEY='dummy-groq-key-for-tests'


class GroqTests(ServiceFixture):
    def projection(self):
        return projection_for(build_service_report(self.root,ServiceRequest(self.request)))

    def test_request_header_schema_endpoint_model_and_cache(self):
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.read.return_value=json.dumps({'choices':[{'finish_reason':'stop','message':{'content':json.dumps(valid_answer())}}]}).encode()
        opener=Mock();opener.open.return_value=response
        advisor=GroqAdvisor(KEY)
        with patch('managerai.gemini_advisor.build_opener',return_value=opener):
            result,cached=advisor.generate(self.projection());self.assertFalse(cached)
            self.assertEqual(result,valid_answer())
            _,cached=advisor.generate(self.projection());self.assertTrue(cached)
        self.assertEqual(opener.open.call_count,1)
        request=opener.open.call_args.args[0]
        self.assertEqual(request.full_url,'https://api.groq.com/openai/v1/chat/completions')
        self.assertEqual(request.get_header('Authorization'),'Bearer '+KEY)
        body=json.loads(request.data)
        self.assertEqual(body['model'],'openai/gpt-oss-120b')
        self.assertTrue(body['response_format']['json_schema']['strict'])
        self.assertNotIn(KEY,request.full_url+request.data.decode())
        sent=json.loads(body['messages'][1]['content'])
        for ref,metric in sent['evidence'].items():
            self.assertNotIn('match_ids',metric)
            for field in ('value','unit','sample_size','definition'):
                self.assertEqual(metric[field],self.projection()['evidence'][ref][field])
        self.assertNotIn('tools',body)
        self.assertNotIn('minItems',json.dumps(body['response_format']))

    def test_limits_and_supported_models(self):
        for model in ['../../bad','https://example.invalid','llama-3.1-8b-instant']:
            with self.assertRaises(ValueError):GroqAdvisor(KEY,model)
        self.assertEqual(GroqAdvisor(KEY,'openai/gpt-oss-20b').model,'openai/gpt-oss-20b')
        with patch('managerai.gemini_advisor.build_opener',side_effect=AssertionError('no network')),self.assertRaises(AdvisorFailure) as error:
            GroqAdvisor(KEY).generate({'large':'x'*16001})
        self.assertEqual(error.exception.code,'INPUT_TOO_LARGE')

    def test_http_429_does_not_retry_or_fallback(self):
        advisor=GroqAdvisor(KEY);opener=Mock();opener.open.side_effect=HTTPError('https://api.groq.com',429,KEY,None,None)
        with patch('managerai.gemini_advisor.build_opener',return_value=opener):
            for _ in range(2):
                with self.assertRaises(AdvisorFailure) as error:advisor.generate(self.projection())
                self.assertEqual(error.exception.code,'RATE_LIMIT')
        self.assertEqual(opener.open.call_count,1)

    def test_auth_failure_and_truncated_output_are_sanitized(self):
        for code in [401,403,503]:
            opener=Mock();opener.open.side_effect=HTTPError('https://api.groq.com',code,KEY,None,None)
            with patch('managerai.gemini_advisor.build_opener',return_value=opener),self.assertRaises(AdvisorFailure) as error:
                GroqAdvisor(KEY).generate(self.projection())
            self.assertNotIn(KEY,str(error.exception))
        response=Mock();response.__enter__=Mock(return_value=response);response.__exit__=Mock(return_value=False)
        response.read.return_value=json.dumps({'choices':[{'finish_reason':'length','message':{'content':json.dumps(valid_answer())}}]}).encode()
        opener=Mock();opener.open.return_value=response
        with patch('managerai.gemini_advisor.build_opener',return_value=opener),self.assertRaises(AdvisorFailure):
            GroqAdvisor(KEY).generate(self.projection())

    def test_declared_provider_rejects_unknown_configuration(self):
        with self.assertRaises(ValueError):backend_environment('/tmp/managerai-no-env',environ={'MANAGERAI_AI_PROVIDER':'other'})
        with self.assertRaises(ValueError):backend_environment('/tmp/managerai-no-env',environ={'MANAGERAI_GROQ_ENABLED':'maybe'})


@unittest.skipUnless(find_spec('fastapi') and find_spec('httpx'),'API opcional')
class GroqAPITests(ServiceFixture):
    def test_explicit_groq_with_both_keys_never_uses_gemini(self):
        from fastapi.testclient import TestClient
        from managerai.api import create_app
        with tempfile.TemporaryDirectory() as td:
            env=Path(td)/'.env'
            env.write_text('GROQ_API_KEY='+KEY+'\nGEMINI_API_KEY=unused-dummy\nMANAGERAI_AI_PROVIDER=groq\nMANAGERAI_GROQ_ENABLED=true\nMANAGERAI_GEMINI_ENABLED=true\n')
            with patch.dict(os.environ,{},clear=True),patch('managerai.api.GeminiAdvisor',side_effect=AssertionError('no fallback')):
                client=TestClient(create_app(data_root=self.root,env_file=env))
            caps=client.get('/v1/capabilities').json()
            self.assertEqual(caps['tactical_advisor']['provider'],'groq')
            self.assertNotIn(KEY,json.dumps(caps))
            with patch('managerai.groq_advisor.GroqAdvisor.generate',return_value=(valid_answer(),False)):
                response=client.post('/v1/analyses',json={'analysis':{'competition_id':2,'season_id':27,'team_id':1,'opponent_id':2,'target_match_id':8},'ai_analysis':'optional'})
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(response.json()['ai_tactical']['provider'],'groq')
            self.assertEqual(response.json()['ai_tactical']['status'],'generated')
            self.assertNotIn(KEY,response.text)
