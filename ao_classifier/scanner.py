"""Parcours récursif du dossier, détection doublons par nom de fichier."""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from ao_classifier.config import IGNORED_FILENAMES, IGNORED_PREFIXES

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    path: Path
    relative: Path
    extension: str
    size_bytes: int
    md5: str
    content_sample: str = ""
    is_duplicate: bool = False
    duplicate_of: Path | None = None


def _is_ignored(path: Path) -> bool:
    name = path.name.lower()
    if name in IGNORED_FILENAMES:
        return True
    return any(name.startswith(p) for p in IGNORED_PREFIXES)



def scan(root: Path) -> list[FileInfo]:
    """Scanne récursivement root et retourne la liste des fichiers."""
    files: list[FileInfo] = []
    seen_names: dict[str, Path] = {}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if _is_ignored(path):
            logger.debug("Ignoré : %s", path.name)
            continue

        relative = path.relative_to(root)
        name_key = path.name.lower()
        is_dup = False
        dup_of = None

        if name_key in seen_names:
            is_dup = True
            dup_of = seen_names[name_key]
            logger.info("Doublon détecté : %s == %s", path.name, dup_of.name)
        else:
            seen_names[name_key] = path

        info = FileInfo(
            path=path,
            relative=relative,
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
            md5="",
            is_duplicate=is_dup,
            duplicate_of=dup_of,
        )
        files.append(info)
        logger.debug("Scanné : %s", relative)

    logger.info("Scan terminé : %d fichiers trouvés", len(files))
    return files
