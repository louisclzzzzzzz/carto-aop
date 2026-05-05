# Carto AO

Outil de classification automatique de dossiers d'appels d'offres utilisant un LLM local via Ollama.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

1. Assurez-vous qu'Ollama est lancé et que le modèle est disponible (ex: `qwen2.5-coder:7b`).
2. Lancez la classification :
   ```bash
   python -m ao_classifier ./mon_dossier_ao
   ```

## Interface Graphique

```bash
streamlit run ao_classifier/gui.py
```
