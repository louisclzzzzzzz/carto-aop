# Carto AO

Outil de classification automatique de dossiers d'appels d'offres (AO) par LLM.  
Supporte deux backends : **Ollama** (local, aucune donnée envoyée) et **Gemini** (cloud, API Google).

---

## Installation

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> Si PowerShell bloque l'exécution de scripts :
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Lancer l'interface graphique

### macOS / Linux

```bash
source .venv/bin/activate
streamlit run ao_classifier/gui.py
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run ao_classifier/gui.py
```

L'interface s'ouvre sur `http://localhost:8501`.

---

## Utilisation de l'interface

### 1. Choisir le fournisseur LLM (sidebar)

| Fournisseur | Prérequis | Données envoyées |
|---|---|---|
| **Ollama (local)** | Ollama installé et `ollama serve` lancé | Aucune — 100% local |
| **Gemini (cloud)** | Clef API Google AI Studio | Contenu des fichiers envoyé à Google |

**Ollama** — sélectionner le modèle (`qwen2.5-coder:7b`, `mistral:7b`…) et vérifier le statut ✓ en bas de la sidebar.

**Gemini** — saisir la clef API (`AIza...`). Créer une clef sur [Google AI Studio](https://aistudio.google.com/app/apikey). Modèles disponibles : `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro`, `gemma-3-27b-it`…

### 2. Régler les paramètres

- **Taille de batch** : nombre de fichiers envoyés par appel LLM (1–10). Réduire si le modèle répond mal.
- **Seuil de confiance** : fichiers en dessous du seuil → dossier `À TRIER`.

### 3. Déposer un ZIP et lancer l'analyse

Glisser-déposer un ZIP du dossier AO (jusqu'à **1 Go**). Cliquer sur **Lancer l'analyse**.

L'interface affiche :
- Un tableau de tous les fichiers avec dossier cible, nom suggéré, confiance et action
- La répartition par dossier (graphique)
- L'arborescence proposée
- Les fichiers à réviser manuellement et les doublons détectés

### 4. Exporter

- **CSV** : listing complet des classements
- **JSON** : plan de réorganisation structuré

---

## CLI (sans interface)

### macOS / Linux

```bash
source .venv/bin/activate
python -m ao_classifier ./mon_dossier_ao --mode dry-run
python -m ao_classifier ./mon_dossier_ao --mode copy --model mistral:7b
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
python -m ao_classifier .\mon_dossier_ao --mode dry-run
python -m ao_classifier .\mon_dossier_ao --mode copy --model mistral:7b
```

Modes disponibles : `dry-run` (simulation), `copy` (copie les fichiers), `move` (déplace les fichiers).

---

## Évaluation de la qualité (optionnel)

Pour mesurer la précision du classifieur sur un dossier dont on connaît la bonne organisation :

### 1. Randomiser le dossier de référence

```bash
# macOS / Linux
python randomize_folder.py AO24

# Windows
python randomize_folder.py AO24
```

Produit `AO24_random/` (noms aléatoires, invisible au LLM) et `AO24_mapping.json` (correspondance).

### 2. Classer le dossier randomisé

Déposer `AO24_random.zip` dans l'interface ou via CLI. Récupérer le fichier `ao_plan_TIMESTAMP.json`.

### 3. Évaluer

```bash
python evaluate.py --ref AO24 --plan ao_plan_TIMESTAMP.json --mapping AO24_mapping.json
```

Affiche la précision globale, par dossier, et le détail des erreurs.

---

## Ollama — installation rapide

### macOS

```bash
brew install ollama
ollama serve
ollama pull qwen2.5-coder:7b
```

### Windows

Télécharger l'installateur sur [ollama.com](https://ollama.com/download/windows), puis dans PowerShell :

```powershell
ollama serve
ollama pull qwen2.5-coder:7b
```
