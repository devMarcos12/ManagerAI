"""Transporte Groq; mesmo contrato, evidências, cache e limites do analisador."""
from copy import deepcopy
from urllib.request import Request

from .explanation import canonical
from .gemini_advisor import GeminiAdvisor, AdvisorFailure, OUTPUT_SCHEMA, SYSTEM


class GroqAdvisor(GeminiAdvisor):
    provider_id = 'groq'
    max_input_bytes = 16000

    def __init__(self, api_key, model='openai/gpt-oss-120b', *, timeout=45):
        super().__init__(api_key, model, timeout=timeout)

    def _valid_model(self, model):
        return model in ('openai/gpt-oss-120b', 'openai/gpt-oss-20b')

    def _encode(self, projection):
        compact = deepcopy(projection)
        # A rastreabilidade integral permanece no relatório; não repetir IDs de
        # partidas e nomes em cada indicador no contexto limitado do plano gratuito.
        for metric in compact.get('evidence', {}).values():
            for key in ('match_ids', 'team_name', 'metric_id'):
                metric.pop(key, None)
        return canonical(compact)

    def _request(self, encoded):
        schema = deepcopy(OUTPUT_SCHEMA)
        # Tamanhos de arrays são conferidos no backend, após geração estruturada.
        def compatible(value):
            if isinstance(value, dict):
                return {k: compatible(v) for k,v in value.items() if k not in ('minItems','maxItems')}
            if isinstance(value, list):
                return [compatible(v) for v in value]
            return value
        body = {'model': self.model, 'messages': [
                    {'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': encoded}],
                'temperature': 0.2, 'max_completion_tokens': 2400, 'stream': False,
                'reasoning_effort': 'low',
                'response_format': {'type': 'json_schema', 'json_schema': {
                    'name': 'tactical_advice', 'strict': True, 'schema': compatible(schema)}}}
        request = Request('https://api.groq.com/openai/v1/chat/completions', canonical(body).encode(),
                          {'Content-Type': 'application/json', 'Accept': 'application/json',
                           'User-Agent': 'ManagerAI/0.1', 'Authorization': 'Bearer ' + self._api_key})
        obj = self._send(request)
        choices = obj.get('choices', [])
        if len(choices) != 1 or choices[0].get('finish_reason') != 'stop':
            raise AdvisorFailure('INVALID_RESPONSE')
        message = choices[0].get('message', {})
        if message.get('refusal') or message.get('tool_calls') or not isinstance(message.get('content'), str):
            raise AdvisorFailure('INVALID_RESPONSE')
        return message['content']
