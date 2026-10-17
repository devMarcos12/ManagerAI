"""Entrada Streamlit; permite iniciar pela raiz sem instalar o pacote ManagerAI."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from managerai.streamlit_ui import main

main()
