"""Criar .env privado sem sobrescrever a configuração pessoal já existente."""
import os
from pathlib import Path


def create_local_env(root):
    root = Path(root)
    template = (root / '.env.example').read_text(encoding='utf-8')
    try:
        descriptor = os.open(root / '.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, 'w', encoding='utf-8') as file:
        file.write(template)
    return True


if __name__ == '__main__':
    created = create_local_env(Path(__file__).resolve().parents[1])
    print('.env criado. Preencha sua chave e confira o plano gratuito antes de ativar o Gemini.'
          if created else '.env existente preservado.')
