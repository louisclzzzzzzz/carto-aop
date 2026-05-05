"""Construction du plan de réorganisation consolidé, résolution de conflits."""

import logging
from dataclasses import dataclass
from pathlib import Path

from ao_classifier.classifier import ClassificationResult
from ao_classifier.utils import sanitize_filename

logger = logging.getLogger(__name__)


@dataclass
class PlanEntry:
    source: Path
    target_folder: str
    suggested_name: str
    destination: Path          # output_root / target_folder / suggested_name
    action: str                # "copy" | "duplicate" | "manual_review"
    confidence: float
    reasoning: str
    original_path: Path        # chemin relatif source


def build_plan(
    results: list[ClassificationResult],
    output_root: Path,
    confidence_threshold: float = 0.7,
) -> list[PlanEntry]:
    """Construit le plan depuis les résultats de classification."""
    entries: list[PlanEntry] = []
    # Suivi des destinations pour détecter les conflits de noms
    used_destinations: dict[Path, int] = {}

    for result in results:
        safe_name = sanitize_filename(result.suggested_name)
        if not safe_name:
            safe_name = sanitize_filename(result.file_info.path.name)

        # Résolution des conflits de noms : ajouter _2, _3...
        dest_dir = output_root / result.target_folder
        dest = dest_dir / safe_name

        if dest in used_destinations:
            used_destinations[dest] += 1
            stem = Path(safe_name).stem
            suffix = Path(safe_name).suffix
            safe_name = f"{stem}_{used_destinations[dest]}{suffix}"
            dest = dest_dir / safe_name
        else:
            used_destinations[dest] = 1

        if result.target_folder == "DOUBLON":
            action = "duplicate"
        elif result.confidence < confidence_threshold:
            action = "manual_review"
        else:
            action = "copy"

        entries.append(PlanEntry(
            source=result.file_info.path,
            target_folder=result.target_folder,
            suggested_name=safe_name,
            destination=dest,
            action=action,
            confidence=result.confidence,
            reasoning=result.reasoning,
            original_path=result.file_info.relative,
        ))

    return entries
