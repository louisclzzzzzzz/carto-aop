#!/usr/bin/env python3
"""
Compare la classification produite par ao_classifier (plan JSON)
avec la structure de référence du dossier AO organisé.

Usage :
    # Avec mapping JSON (rapide, produit par randomize_folder.py) :
    python evaluate.py --ref AO24 --plan ao_plan_TIMESTAMP.json --mapping AO24_mapping.json

    # Sans mapping : matching par MD5 (plus lent, ~1 min sur 300 fichiers) :
    python evaluate.py --ref AO24 --plan ao_plan_TIMESTAMP.json
"""

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


def md5(path: Path) -> str:
    h = hashlib.md5()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""


def build_ref_index(ref_root: Path) -> dict[str, str]:
    """MD5 → dossier de référence (ex: 'TECH/CCTP')."""
    index: dict[str, str] = {}
    for p in ref_root.rglob("*"):
        if not p.is_file() or p.name.startswith("."):
            continue
        h = md5(p)
        if h:
            rel = p.relative_to(ref_root)
            # Le dossier de référence = tout sauf le nom du fichier
            folder = str(rel.parent) if str(rel.parent) != "." else "(racine)"
            index[h] = folder
    return index


def normalize_folder(folder: str) -> str:
    """Normalise pour comparaison : casse, slashes."""
    return folder.strip().replace("\\", "/").upper()


def top_level(folder: str) -> str:
    """Premier niveau du chemin (ex: 'TECH/CCTP' → 'TECH')."""
    return folder.split("/")[0]


def build_ref_index_from_mapping(mapping_path: Path, ref_root: Path) -> dict[str, str]:
    """nom_aléatoire → dossier de référence, via le mapping JSON de randomize_folder.py."""
    raw: dict[str, str] = json.loads(mapping_path.read_text(encoding="utf-8"))
    index: dict[str, str] = {}
    for random_name, original_rel in raw.items():
        folder = str(Path(original_rel).parent)
        index[random_name] = folder if folder != "." else "(racine)"
    return index


def main() -> None:
    parser = argparse.ArgumentParser(description="Évalue la qualité du classement AO")
    parser.add_argument("--ref", required=True, help="Dossier AO de référence (ex: AO24)")
    parser.add_argument("--plan", required=True, help="Plan JSON produit par ao_classifier")
    parser.add_argument(
        "--mapping",
        help="Mapping JSON produit par randomize_folder.py (plus rapide que MD5)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Comparaison stricte (chemin complet) ; par défaut compare le 1er niveau seulement",
    )
    args = parser.parse_args()

    ref_root = Path(args.ref)
    plan_path = Path(args.plan)

    if not ref_root.is_dir():
        sys.exit(f"Dossier de référence introuvable : {ref_root}")
    if not plan_path.is_file():
        sys.exit(f"Fichier plan introuvable : {plan_path}")

    print(f"📂 Référence  : {ref_root}")
    print(f"📋 Plan       : {plan_path}")

    use_mapping = args.mapping and Path(args.mapping).is_file()

    if use_mapping:
        print(f"🗺️  Mapping    : {args.mapping}")
        # index : nom_aléatoire → dossier_référence
        ref_index = build_ref_index_from_mapping(Path(args.mapping), ref_root)
        lookup_key = "filename"  # on recherche par nom de fichier
    else:
        print("⏳ Calcul des hash MD5 de référence…")
        ref_index = build_ref_index(ref_root)
        lookup_key = "md5"

    print(f"   {len(ref_index)} fichiers indexés\n")

    plan_data = json.loads(plan_path.read_text(encoding="utf-8"))
    entries = plan_data if isinstance(plan_data, list) else plan_data.get("entries", [])

    matched = 0
    unmatched_in_ref = 0
    correct = 0
    wrong = 0
    skipped_action = 0  # doublons / manual_review non évalués

    errors: list[dict] = []
    per_folder_correct: dict[str, int] = defaultdict(int)
    per_folder_total: dict[str, int] = defaultdict(int)
    confusion: dict[tuple[str, str], int] = defaultdict(int)

    for entry in entries:
        action = entry.get("action", "copy")
        source_path = Path(entry.get("source", entry.get("original_path", "")))
        predicted = entry.get("target_folder", "")

        # Doublons et manual_review : on les compte mais on n'évalue pas
        if action in ("duplicate",):
            skipped_action += 1
            continue

        if not source_path.exists():
            unmatched_in_ref += 1
            continue

        if lookup_key == "filename":
            key = source_path.name
        else:
            key = md5(source_path)

        if not key or key not in ref_index:
            unmatched_in_ref += 1
            continue

        matched += 1
        truth = ref_index[key]

        if args.strict:
            is_correct = normalize_folder(predicted) == normalize_folder(truth)
        else:
            is_correct = top_level(normalize_folder(predicted)) == top_level(normalize_folder(truth))

        per_folder_total[top_level(normalize_folder(truth))] += 1

        if is_correct:
            correct += 1
            per_folder_correct[top_level(normalize_folder(truth))] += 1
        else:
            wrong += 1
            confusion[(top_level(normalize_folder(truth)), top_level(normalize_folder(predicted)))] += 1
            errors.append({
                "fichier": source_path.name,
                "vérité": truth,
                "prédit": predicted,
                "confiance": entry.get("confidence", 0),
            })

    # ─── Résultats ───────────────────────────────────────────────────────────
    total_eval = correct + wrong
    accuracy = correct / total_eval * 100 if total_eval else 0

    print("=" * 60)
    print("  RÉSULTATS D'ÉVALUATION")
    print("=" * 60)
    print(f"  Entrées dans le plan       : {len(entries)}")
    print(f"  Évalués (matchés MD5)      : {matched}")
    print(f"  Non matchés / introuvables : {unmatched_in_ref}")
    print(f"  Doublons (non évalués)     : {skipped_action}")
    print()
    mode = "strict (chemin complet)" if args.strict else "souple (1er niveau)"
    print(f"  Mode de comparaison : {mode}")
    print(f"  ✅ Corrects  : {correct}/{total_eval}")
    print(f"  ❌ Erronés   : {wrong}/{total_eval}")
    print(f"  🎯 Précision : {accuracy:.1f}%")
    print()

    # ─── Par dossier ─────────────────────────────────────────────────────────
    print("─" * 60)
    print("  PAR DOSSIER (niveau 1)")
    print("─" * 60)
    all_folders = sorted(per_folder_total.keys())
    for folder in all_folders:
        tot = per_folder_total[folder]
        ok = per_folder_correct.get(folder, 0)
        pct = ok / tot * 100 if tot else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {folder:<25} {bar} {ok:>3}/{tot:<3} ({pct:.0f}%)")
    print()

    # ─── Confusions fréquentes ────────────────────────────────────────────────
    if confusion:
        print("─" * 60)
        print("  CONFUSIONS FRÉQUENTES (vérité → prédit)")
        print("─" * 60)
        for (truth, pred), count in sorted(confusion.items(), key=lambda x: -x[1])[:10]:
            print(f"  {truth:<20} → {pred:<20}  × {count}")
        print()

    # ─── Détail des erreurs ───────────────────────────────────────────────────
    if errors:
        print("─" * 60)
        print(f"  DÉTAIL DES ERREURS ({len(errors)} fichiers mal classés)")
        print("─" * 60)
        for e in sorted(errors, key=lambda x: x["confiance"], reverse=True):
            conf = f"{e['confiance']*100:.0f}%"
            print(f"  [{conf:>4}] {e['fichier'][:40]:<40}")
            print(f"         Vérité : {e['vérité']}")
            print(f"         Prédit : {e['prédit']}")
        print()

    print("=" * 60)


if __name__ == "__main__":
    main()
