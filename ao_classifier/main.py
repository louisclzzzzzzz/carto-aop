"""Orchestration des 7 étapes du classificateur AO."""

import logging
import signal
import sys
from pathlib import Path

from ao_classifier.classifier import check_ollama, classify_all
from ao_classifier.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_MODEL,
    OLLAMA_BASE_URL,
)
from ao_classifier.executor import execute_plan
from ao_classifier.extractor import enrich_files
from ao_classifier.planner import build_plan
from ao_classifier.reporter import generate_report, load_plan_from_json
from ao_classifier.scanner import scan
from ao_classifier.utils import open_in_editor, timestamp

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool, log_path: Path) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers: list[logging.Handler] = [
        logging.FileHandler(log_path, encoding="utf-8"),
    ]
    if verbose:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def _sigint_handler(sig, frame):
    print("\n\nInterruption détectée — aucune modification effectuée.", flush=True)
    sys.exit(0)


def run(
    input_folder: Path,
    output_folder: Path | None,
    mode: str,
    model: str,
    batch_size: int,
    confidence_threshold: float,
    plan_file: Path | None,
    no_confirm: bool,
    verbose: bool,
) -> None:
    signal.signal(signal.SIGINT, _sigint_handler)

    ts = timestamp()
    log_path = Path(f"ao_classifier_{ts}.log")
    _setup_logging(verbose, log_path)

    output_root = output_folder or input_folder.parent / f"{input_folder.name}_organized"
    report_path = Path(f"ao_plan_{ts}.md")
    plan_json_path = Path(f"ao_plan_{ts}.json")

    print(f"\n=== ao_classifier ===")
    print(f"Dossier source  : {input_folder}")
    print(f"Dossier cible   : {output_root}")
    print(f"Mode            : {mode}")
    print(f"Modèle Ollama   : {model}")
    print()

    # Étape 1 : vérification Ollama (sauf si plan externe fourni)
    if plan_file is None:
        if not check_ollama(OLLAMA_BASE_URL):
            print(
                "❌ Ollama n'est pas accessible sur http://localhost:11434\n"
                "   Lancez : ollama serve\n"
                "   Puis tirez votre modèle : ollama pull qwen2.5-coder:7b"
            )
            sys.exit(1)
        print("✓ Ollama accessible\n")

    if plan_file:
        # Charger un plan JSON existant
        print(f"Chargement du plan depuis : {plan_file}")
        entries = load_plan_from_json(plan_file, output_root)
    else:
        # Étape 1 — Scan
        print("Étape 1/5 — Scan du dossier...")
        files = scan(input_folder)
        print(f"  {len(files)} fichier(s) trouvé(s)")

        # Étape 2 — Extraction
        print("Étape 2/5 — Extraction du contenu...")
        files = enrich_files(files)

        # Étape 3 — Classement LLM
        print(f"Étape 3/5 — Classement via Ollama ({model})...")
        results = classify_all(
            files,
            model=model,
            base_url=OLLAMA_BASE_URL,
            batch_size=batch_size,
            confidence_threshold=confidence_threshold,
        )

        # Étape 4 — Plan
        print("Étape 4/5 — Construction du plan...")
        entries = build_plan(results, output_root, confidence_threshold)

        # Étape 5 — Rapport
        print("Étape 5/5 — Génération du rapport...")
        report_content = generate_report(
            entries,
            input_root=input_folder,
            output_root=output_root,
            report_path=report_path,
            plan_json_path=plan_json_path,
            confidence_threshold=confidence_threshold,
        )
        print()
        print(report_content[:3000])
        if len(report_content) > 3000:
            print(f"... (rapport tronqué — voir {report_path})")
        print()

    # Étape 6 — Validation interactive
    if not no_confirm:
        print(f"Plan généré : {plan_json_path}")
        print(f"Rapport     : {report_path}\n")

        while True:
            choice = input(
                "Voulez-vous exécuter ce plan ?\n"
                "  [o] Oui — exécuter\n"
                "  [n] Non — annuler\n"
                "  [e] Éditer le JSON puis relancer avec --plan\n"
                "Votre choix : "
            ).strip().lower()

            if choice == "o":
                break
            elif choice == "n":
                print("Annulé — aucune modification effectuée.")
                sys.exit(0)
            elif choice == "e":
                open_in_editor(plan_json_path)
                print(
                    f"\nFichier JSON ouvert pour édition.\n"
                    f"Après modification, relancez avec :\n"
                    f"  python -m ao_classifier {input_folder} --plan {plan_json_path}\n"
                )
                sys.exit(0)

    # Étape 7 — Exécution
    if mode == "move":
        confirm = input(
            "⚠️  Mode MOVE : les fichiers sources seront DÉPLACÉS (irréversible).\n"
            "Confirmer ? [oui/non] : "
        ).strip().lower()
        if confirm != "oui":
            print("Annulé.")
            sys.exit(0)

    exec_log = Path(f"ao_classifier_{ts}.log")
    print(f"\nExécution en mode '{mode}'...")
    counters = execute_plan(entries, mode=mode, log_path=exec_log)

    print(
        f"\n✓ Terminé — {counters['copy']} fichier(s) traité(s), "
        f"{counters['skip']} ignoré(s), {counters['error']} erreur(s)"
    )
    print(f"Journal : {exec_log}")
