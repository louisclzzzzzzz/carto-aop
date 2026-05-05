"""Parcours récursif du dossier, hash MD5, détection doublons."""

import hashlib
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


def _md5(path: Path) -> str:
    h = hashlib.md5()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        logger.warning("Impossible de hasher %s : %s", path, e)
        return ""


def scan(root: Path) -> list[FileInfo]:
    """Scanne récursivement root et retourne la liste des fichiers."""
    files: list[FileInfo] = []
    seen_md5: dict[str, Path] = {}

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if _is_ignored(path):
            logger.debug("Ignoré : %s", path.name)
            continue

        relative = path.relative_to(root)
        md5 = _md5(path)
        is_dup = False
        dup_of = None

        if md5 and md5 in seen_md5:
            is_dup = True
            dup_of = seen_md5[md5]
            logger.info("Doublon détecté : %s == %s", path.name, dup_of.name)
        elif md5:
            seen_md5[md5] = path

        info = FileInfo(
            path=path,
            relative=relative,
            extension=path.suffix.lower(),
            size_bytes=path.stat().st_size,
            md5=md5,
            is_duplicate=is_dup,
            duplicate_of=dup_of,
        )
        files.append(info)
        logger.debug("Scanné : %s (%s)", relative, md5[:8] if md5 else "?")

    logger.info("Scan terminé : %d fichiers trouvés", len(files))
    return files
