#!/usr/bin/env python3
"""
Randomise un dossier AO pour évaluation du classifieur.

- Copie tous les fichiers dans un dossier plat avec des noms aléatoires
- Conserve les extensions (nécessaires au classifieur)
- Sauvegarde un mapping JSON *hors* du dossier randomisé (invisible au LLM)

Usage :
    python randomize_folder.py AO24
    python randomize_folder.py AO24 --out AO24_random --mapping AO24_mapping.json
"""

import argparse
import json
import shutil
import string
import random
from pathlib import Path


IGNORED = {".ds_store", "thumbs.db", "desktop.ini"}
RANDOM_NAME_LENGTH = 12
RANDOM_CHARS = string.ascii_letters + string.digits


def random_name(length: int = RANDOM_NAME_LENGTH) -> str:
    return "".join(random.choices(RANDOM_CHARS, k=length))


def collect_files(root: Path) -> list[Path]:
    return [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and p.name.lower() not in IGNORED and not p.name.startswith(".")
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Randomise un dossier AO pour évaluation")
    parser.add_argument("source", help="Dossier source à randomiser (ex: AO24)")
    parser.add_argument("--out", help="Dossier de sortie (défaut: <source>_random)")
    parser.add_argument(
        "--mapping",
        help="Fichier de mapping JSON (défaut: <source>_mapping.json)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Graine aléatoire pour reproductibilité",
    )
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_dir():
        raise SystemExit(f"Dossier source introuvable : {source}")

    out_dir = Path(args.out) if args.out else source.parent / f"{source.name}_random"
    mapping_path = (
        Path(args.mapping) if args.mapping
        else source.parent / f"{source.name}_mapping.json"
    )

    if out_dir.exists():
        raise SystemExit(
            f"Le dossier de sortie existe déjà : {out_dir}\n"
            "Supprimez-le ou choisissez un autre nom avec --out."
        )

    if args.seed is not None:
        random.seed(args.seed)

    files = collect_files(source)
    print(f"📂 Source      : {source}  ({len(files)} fichiers)")
    print(f"📁 Sortie      : {out_dir}")
    print(f"🗺️  Mapping     : {mapping_path}")
    print()

    out_dir.mkdir(parents=True)

    # Garantit l'unicité des noms aléatoires
    used_names: set[str] = set()
    mapping: dict[str, str] = {}  # nom_aléatoire → chemin_relatif_original

    for src_path in files:
        ext = src_path.suffix  # ex: ".pdf"
        # Générer un nom unique
        while True:
            name = random_name() + ext
            if name not in used_names:
                used_names.add(name)
                break

        dst_path = out_dir / name
        shutil.copy2(src_path, dst_path)

        rel = str(src_path.relative_to(source))
        mapping[name] = rel
        print(f"  {rel:<60} → {name}")

    # Mapping sauvegardé HORS du dossier randomisé
    mapping_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print()
    print(f"✅ {len(files)} fichiers copiés dans {out_dir}")
    print(f"🗺️  Mapping sauvegardé : {mapping_path}")
    print()
    print("Pour évaluer après classification :")
    print(f"  python evaluate.py --ref {source} --plan ao_plan_TIMESTAMP.json")
    print(f"  # ou via le mapping :")
    print(f"  python evaluate.py --ref {source} --plan ao_plan_TIMESTAMP.json --mapping {mapping_path}")


if __name__ == "__main__":
    main()
