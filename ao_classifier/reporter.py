"""Génération du rapport Markdown et export du plan JSON."""

import json
import logging
from collections import defaultdict
from pathlib import Path

from ao_classifier.planner import PlanEntry
from ao_classifier.utils import human_size, timestamp

logger = logging.getLogger(__name__)


def _build_ascii_tree(entries: list[PlanEntry]) -> str:
    """Construit une arborescence ASCII de la destination proposée."""
    tree: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        if e.action != "duplicate":
            tree[e.target_folder].append(e.suggested_name)

    lines = ["<dossier_organized>/"]
    for folder in sorted(tree.keys()):
        lines.append(f"├── {folder}/")
        files = sorted(tree[folder])
        for i, fname in enumerate(files):
            connector = "└── " if i == len(files) - 1 else "├── "
            lines.append(f"│   {connector}{fname}")
    return "\n".join(lines)


def generate_report(
    entries: list[PlanEntry],
    input_root: Path,
    output_root: Path,
    report_path: Path,
    plan_json_path: Path,
    confidence_threshold: float = 0.7,
) -> str:
    """Génère le rapport Markdown et le fichier JSON du plan."""
    total = len(entries)
    duplicates = [e for e in entries if e.action == "duplicate"]
    manual = [e for e in entries if e.action == "manual_review"]
    classified = [e for e in entries if e.action == "copy"]

    ts = timestamp()
    lines: list[str] = [
        f"# Rapport ao_classifier — {ts}",
        "",
        f"**Dossier source :** `{input_root}`",
        f"**Dossier cible :** `{output_root}`",
        "",
        "## Résumé",
        "",
        f"| Indicateur | Valeur |",
        f"|---|---|",
        f"| Total fichiers | {total} |",
        f"| Classés avec confiance ≥ {confidence_threshold} | {len(classified)} |",
        f"| À réviser manuellement | {len(manual)} |",
        f"| Doublons détectés | {len(duplicates)} |",
        "",
        "## Arborescence proposée",
        "",
        "```",
        _build_ascii_tree(entries),
        "```",
        "",
        "## Détail des classements",
        "",
        "| Fichier source | Dossier cible | Nouveau nom | Confiance | Raison |",
        "|---|---|---|---|---|",
    ]

    for e in sorted(entries, key=lambda x: x.target_folder):
        conf_str = f"{e.confidence:.0%}"
        source_str = str(e.original_path)
        lines.append(
            f"| {source_str} | {e.target_folder} | {e.suggested_name} | {conf_str} | {e.reasoning} |"
        )

    if manual:
        lines += [
            "",
            "## ⚠️ À RÉVISER MANUELLEMENT",
            "",
            f"Ces {len(manual)} fichiers ont une confiance < {confidence_threshold:.0%} :",
            "",
        ]
        for e in manual:
            lines.append(f"- `{e.original_path}` → suggestion : `{e.target_folder}/{e.suggested_name}` ({e.confidence:.0%})")

    if duplicates:
        lines += [
            "",
            "## 🗑️ DOUBLONS DÉTECTÉS",
            "",
            "Ces fichiers sont des doublons (même contenu MD5) — à supprimer manuellement après vérification :",
            "",
        ]
        for e in duplicates:
            lines.append(f"- `{e.original_path}`")

    report_content = "\n".join(lines)
    report_path.write_text(report_content, encoding="utf-8")
    logger.info("Rapport sauvegardé : %s", report_path)

    # Export JSON du plan pour édition manuelle possible
    plan_data = [
        {
            "source": str(e.source),
            "original_path": str(e.original_path),
            "target_folder": e.target_folder,
            "suggested_name": e.suggested_name,
            "action": e.action,
            "confidence": e.confidence,
            "reasoning": e.reasoning,
        }
        for e in entries
    ]
    plan_json_path.write_text(
        json.dumps({"entries": plan_data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Plan JSON sauvegardé : %s", plan_json_path)

    return report_content


def load_plan_from_json(plan_json_path: Path, output_root: Path) -> list[PlanEntry]:
    """Recharge un plan depuis un fichier JSON édité manuellement."""
    data = json.loads(plan_json_path.read_text(encoding="utf-8"))
    entries = []
    for item in data["entries"]:
        entries.append(PlanEntry(
            source=Path(item["source"]),
            target_folder=item["target_folder"],
            suggested_name=item["suggested_name"],
            destination=output_root / item["target_folder"] / item["suggested_name"],
            action=item["action"],
            confidence=item["confidence"],
            reasoning=item["reasoning"],
            original_path=Path(item["original_path"]),
        ))
    return entries
