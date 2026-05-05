"""Application du plan de réorganisation (copy / move / dry-run) avec journal."""

import logging
import shutil
from pathlib import Path

from ao_classifier.planner import PlanEntry

logger = logging.getLogger(__name__)


def execute_plan(
    entries: list[PlanEntry],
    mode: str,
    log_path: Path,
) -> dict[str, int]:
    """
    Exécute le plan selon le mode choisi.
    mode : "copy" | "move" | "dry-run"
    Retourne un dict de compteurs {copy, skip, error}.
    """
    counters = {"copy": 0, "skip": 0, "error": 0}

    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(f"# Journal ao_classifier — mode={mode}\n\n")

        for entry in entries:
            if entry.action == "duplicate":
                msg = f"[DUPLICATE] {entry.source} (doublon)\n"
                log_file.write(msg)
                logger.info("DOUBLON ignoré : %s", entry.source.name)
                counters["skip"] += 1
                continue

            if mode == "dry-run":
                msg = f"[DRY-RUN] {entry.source} → {entry.destination}\n"
                log_file.write(msg)
                logger.info("DRY-RUN : %s → %s", entry.source.name, entry.destination)
                counters["copy"] += 1
                continue

            try:
                entry.destination.parent.mkdir(parents=True, exist_ok=True)

                if mode == "copy":
                    shutil.copy2(str(entry.source), str(entry.destination))
                    msg = f"[COPY] {entry.source} → {entry.destination}\n"
                    log_file.write(msg)
                    logger.info("Copié : %s → %s", entry.source.name, entry.destination)
                    counters["copy"] += 1

                elif mode == "move":
                    shutil.move(str(entry.source), str(entry.destination))
                    msg = f"[MOVE] {entry.source} → {entry.destination}\n"
                    log_file.write(msg)
                    logger.info("Déplacé : %s → %s", entry.source.name, entry.destination)
                    counters["copy"] += 1

            except OSError as e:
                msg = f"[ERROR] {entry.source} → {entry.destination} : {e}\n"
                log_file.write(msg)
                logger.error("Erreur lors de %s sur %s : %s", mode, entry.source.name, e)
                counters["error"] += 1

        log_file.write(
            f"\n# Résumé : {counters['copy']} traités, "
            f"{counters['skip']} ignorés, {counters['error']} erreurs\n"
        )

    return counters
