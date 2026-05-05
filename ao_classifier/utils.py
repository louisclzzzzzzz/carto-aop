"""Fonctions utilitaires partagées."""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Caractères interdits dans les noms de fichiers Windows
_FORBIDDEN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_MULTI_SPACES = re.compile(r'\s+')
_TRAILING_DOTS_SPACES = re.compile(r'[\s.]+$')


def sanitize_filename(name: str) -> str:
    """Normalise un nom de fichier pour compatibilité Windows/macOS."""
    name = _FORBIDDEN_CHARS.sub('_', name)
    name = _MULTI_SPACES.sub(' ', name)
    name = _TRAILING_DOTS_SPACES.sub('', name)
    # Noms réservés Windows
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    stem = Path(name).stem.upper()
    if stem in reserved:
        name = f"_{name}"
    return name.strip()


def open_in_editor(path: Path) -> None:
    """Ouvre un fichier dans l'éditeur par défaut du système."""
    import os
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        subprocess.run([editor, str(path)])
    elif sys.platform == "win32":
        subprocess.run(["notepad.exe", str(path)])
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])


def human_size(size_bytes: int) -> str:
    """Convertit une taille en octets en chaîne lisible."""
    for unit in ("o", "Ko", "Mo", "Go"):
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} To"
