"""Configuração local restrita ao backend; nunca imprime valores de credenciais."""
from pathlib import Path
import os
import re

_ALLOWED = frozenset(('GROQ_API_KEY', 'MANAGERAI_GROQ_MODEL', 'MANAGERAI_GROQ_ENABLED',
                      'MANAGERAI_AI_PROVIDER', 'GEMINI_API_KEY', 'MANAGERAI_GEMINI_MODEL', 'MANAGERAI_GEMINI_ENABLED',
                      'MANAGERAI_DATA_ROOT', 'MANAGERAI_CORS_ORIGINS', 'MANAGERAI_OLLAMA_MODEL',
                      'MANAGERAI_OLLAMA_DIGEST'))


def backend_environment(path=None, *, environ=None):
    env = dict(os.environ if environ is None else environ)
    target = Path(path or env.get('MANAGERAI_ENV_FILE', '.env'))
    # Deliberadamente não executa shell, interpolação, escapes ou comandos.
    if target.is_file() and target.stat().st_size > 16000:
        raise ValueError('Arquivo de configuração local excede o limite.')
    parsed = {}
    content = target.read_text(encoding='utf-8-sig') if target.is_file() else ''
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:].strip()
        key, separator, value = line.partition('=')
        key, value = key.strip(), value.strip()
        if not separator or not re.fullmatch(r'[A-Z][A-Z0-9_]*', key):
            raise ValueError('Formato inválido no arquivo de configuração local.')
        if key not in _ALLOWED:
            continue
        if value.startswith(('"', "'")):
            quote = value[0]
            end = value.find(quote, 1)
            if end < 0 or value[end + 1:].strip() and not value[end + 1:].strip().startswith('#'):
                raise ValueError('Valor inválido no arquivo de configuração local.')
            value = value[1:end]
        else:
            value = re.split(r'\s+#', value, maxsplit=1)[0].rstrip()
        if key in parsed:
            raise ValueError('Variável duplicada no arquivo de configuração local.')
        parsed[key] = value
    for key, value in parsed.items():
        env.setdefault(key, value)  # ambiente exportado prevalece, inclusive vazio
    if env.get('MANAGERAI_AI_PROVIDER', 'gemini') not in ('gemini', 'groq'):
        raise ValueError('MANAGERAI_AI_PROVIDER deve ser gemini ou groq.')
    for name in ('MANAGERAI_GEMINI_ENABLED', 'MANAGERAI_GROQ_ENABLED'):
        if env.get(name, 'false').lower() not in ('true', 'false'):
            raise ValueError(name + ' deve ser true ou false.')
    return env
