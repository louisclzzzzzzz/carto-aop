# ao-classifier — Projet Python CLI

## Rôle du projet
Script Python CLI local qui analyse un dossier d'appel d'offres (AO) désorganisé,
propose un plan de réorganisation structuré, attend validation humaine, puis exécute.
Le LLM de classement tourne en local via Ollama (API compatible Anthropic).

## Stack technique
- Python 3.10+ / pathlib strict / type hints partout
- LLM : Ollama via openai-compatible REST (http://localhost:11434)
- PDF : pypdf (texte natif), pdfplumber (fallback)
- DOCX : python-docx
- XLSX : openpyxl
- CLI : argparse
- Config : .env + python-dotenv

## Conventions de code
- Tous les chemins via pathlib.Path, jamais os.path
- Encoding UTF-8 strict partout (noms de fichiers français avec accents)
- Logging via le module logging standard (pas de print sauf CLI)
- Aucune suppression de fichier source en mode par défaut
- Fonctions courtes, une responsabilité chacune
- Commentaires en français

## Architecture des modules
- main.py          → Entrée CLI (argparse)
- config.py        → Constantes, template arbo, glossaire métier
- scanner.py       → Parcours récursif, hash MD5, détection doublons
- extractor.py     → Extraction texte (PDF/DOCX/XLSX/archives)
- classifier.py    → Appel Ollama pour classement + renommage (JSON)
- planner.py       → Construction plan de réorganisation consolidé
- reporter.py      → Rapport Markdown (arbo ASCII, tableau, alertes)
- executor.py      → Application du plan (copy/move) avec journal
- utils.py         → Fonctions utilitaires partagées

## Commandes utiles
python -m ao_classifier --help
python -m ao_classifier ./dossier_ao --mode dry-run
python -m ao_classifier ./dossier_ao --mode copy --model qwen2.5-coder:7b
pytest tests/ -v

## Contraintes importantes
- Compatible Windows (SMA BTP) ET macOS (développement)
- Ollama doit tourner sur localhost:11434
- Le modèle local a un contexte limité → envoyer max 2000 chars par fichier
- Batch de 5 fichiers max par appel LLM (modèles locaux < 64k tokens)
- Toujours journaliser les actions dans ao_classifier_TIMESTAMP.log
- Mode copy par défaut : ne jamais déplacer les sources sans --mode move explicite