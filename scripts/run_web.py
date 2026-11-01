"""Iniciar API e frontend locais; encerrar somente os processos deste comando."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from setup_env import create_local_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=".venv-web/bin/python", help="Python do ambiente isolado com ManagerAI instalado")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # Preservar o caminho do venv: resolve() seguiria o symlink até o Python
    # do sistema e perderia as dependências instaladas no ambiente escolhido.
    interpreter = (root / args.python).absolute()
    if not interpreter.is_file() or not (root/"frontend/node_modules/.bin/vite").exists():
        parser.error("Instale .venv-web com .[api,v3] e execute npm ci em frontend, conforme README.")
    version = subprocess.check_output(["node", "--version"], text=True).strip()
    numbers = tuple(int(n) for n in version.lstrip("v").split(".")[:2])
    if not (numbers >= (22,12) or numbers[0] == 20 and numbers >= (20,19)):
        parser.error("Use Node 20.19+ ou 22.12+. Consulte frontend/.nvmrc.")
    if create_local_env(root):
        print('.env criado. Preencha sua chave pessoal; A IA permanece desativada até sua ativação explícita.', flush=True)
    env = {**os.environ, "MANAGERAI_ENV_FILE": str(root / '.env'),
           "MANAGERAI_PROXY_TARGET": "http://127.0.0.1:8011", "PYTHONDONTWRITEBYTECODE": "1"}
    processes = []
    try:
        processes.append(subprocess.Popen([str(interpreter), "-I", "-B", "-m", "uvicorn", "managerai.api:create_app", "--factory",
                          "--host", "127.0.0.1", "--port", "8011", "--workers", "1", "--no-access-log"], cwd=root, env=env, start_new_session=True))
        processes.append(subprocess.Popen(["npm", "run", "dev"], cwd=root/"frontend", env={k: v for k, v in env.items() if k not in ("GEMINI_API_KEY", "GROQ_API_KEY", "MANAGERAI_ENV_FILE") and not k.startswith(("MANAGERAI_GEMINI_", "MANAGERAI_GROQ_"))}, start_new_session=True))
        print("Abra http://127.0.0.1:5173 — Ctrl+C encerra estes dois processos.", flush=True)
        while all(p.poll() is None for p in processes):
            time.sleep(.3)
        return next((p.returncode for p in processes if p.returncode is not None), 1)
    except KeyboardInterrupt:
        return 0
    finally:
        for p in processes:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGTERM)
        for p in processes:
            try:
                p.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()


if __name__ == "__main__":
    sys.exit(main())

