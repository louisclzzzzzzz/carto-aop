"""Point d'entrée : python -m ao_classifier"""

import argparse
import sys
from pathlib import Path

from ao_classifier.config import DEFAULT_BATCH_SIZE


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ao_classifier",
        description="Classificateur de dossiers Appel d'Offres (AO) via LLM local Ollama",
    )
    parser.add_argument("input_folder", type=Path, help="Dossier AO à analyser")
    parser.add_argument(
        "--output", type=Path, default=None, metavar="PATH",
        help="Dossier de sortie (défaut : <input>_organized)"
    )
    parser.add_argument(
        "--mode", choices=["copy", "move", "dry-run"], default="copy",
        help="Mode d'exécution (défaut : copy)"
    )
    parser.add_argument(
        "--model", default="qwen2.5-coder:7b", metavar="NAME",
        help="Modèle Ollama pour le classement (défaut : qwen2.5-coder:7b)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_BATCH_SIZE, metavar="N",
        help=f"Fichiers par appel LLM (défaut : {DEFAULT_BATCH_SIZE}, max : 10)"
    )
    parser.add_argument(
        "--confidence-threshold", type=float, default=0.7, metavar="F",
        help="Seuil de confiance pour révision manuelle (défaut : 0.7)"
    )
    parser.add_argument(
        "--plan", type=Path, default=None, metavar="PATH",
        help="Charger un plan JSON existant au lieu de recalculer"
    )
    parser.add_argument(
        "--no-confirm", action="store_true",
        help="Sauter la validation interactive"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Logs détaillés dans le terminal"
    )

    args = parser.parse_args()

    if not args.input_folder.is_dir():
        print(f"Erreur : '{args.input_folder}' n'est pas un dossier valide.", file=sys.stderr)
        sys.exit(1)

    batch_size = min(max(args.batch_size, 1), 10)

    from ao_classifier.main import run
    run(
        input_folder=args.input_folder.resolve(),
        output_folder=args.output.resolve() if args.output else None,
        mode=args.mode,
        model=args.model,
        batch_size=batch_size,
        confidence_threshold=args.confidence_threshold,
        plan_file=args.plan,
        no_confirm=args.no_confirm,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
