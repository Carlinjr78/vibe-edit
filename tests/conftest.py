"""Deixa os modulos de scripts/ importaveis nos testes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
