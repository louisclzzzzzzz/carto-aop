# AO Classifier

> LLM-powered tool that automatically sorts and renames the documents inside a French construction-tender (Appel d'Offres) archive into a clean, standardised folder structure.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-local%20LLM-black?logo=ollama&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-Google%20AI-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What it does

Construction project managers receive tender packages (DCE) as disorganised ZIP archives — dozens of PDFs, DOCX files, and spreadsheets with cryptic names. AO Classifier:

- Extracts and reads every document (PDF, DOCX, XLSX, nested ZIPs)
- Sends batches to an LLM (local or cloud) to identify each file's type
- Assigns each file a target folder and a suggested human-readable name
- Produces a structured reorganisation plan (JSON + Markdown report)
- Applies the plan with a `copy` or `move` operation — source files are never touched by default

## Key features

- **Privacy-first option** — run fully offline with Ollama; no document content leaves your machine
- **Multi-backend** — Ollama (local), Gemini (Google AI Studio), or Mistral
- **Streamlit GUI** — drag-and-drop ZIP, review results in a table, export CSV/JSON
- **CLI** — scriptable, supports `dry-run` / `copy` / `move` modes
- **Evaluation tooling** — scripts to scramble a reference folder and measure classifier accuracy

---

## Project structure

```
ao_classifier/       # main Python package (pipeline)
  __main__.py        # CLI entry point
  config.py          # folder taxonomy, LLM constants
  scanner.py         # recursive walk, MD5 dedup
  extractor.py       # PDF / DOCX / XLSX / archive text extraction
  classifier.py      # LLM calls (Ollama / Gemini / Mistral)
  planner.py         # build reorganisation plan
  reporter.py        # Markdown report + ASCII tree
  executor.py        # apply plan, write audit log
  gui.py             # Streamlit front-end
scripts/
  randomize_folder.py   # scramble a reference folder for evaluation
  evaluate.py           # compare classifier output vs. ground truth
  generate_fake_ao.py   # generate synthetic test data
requirements.txt
.env.example
```

---

## Installation

```bash
git clone <repo-url>
cd classifier_aop

python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **Windows note:** if PowerShell blocks script execution, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Usage

### Streamlit GUI

```bash
source .venv/bin/activate
streamlit run ao_classifier/gui.py
# opens http://localhost:8501
```

Drop a ZIP into the interface, pick your LLM backend in the sidebar, and click **Run analysis**.

### CLI

```bash
# Dry run — preview only, no files touched
python -m ao_classifier ./my_tender_folder --mode dry-run

# Copy files into the new structure (safe default)
python -m ao_classifier ./my_tender_folder --mode copy --model qwen2.5-coder:7b

# Move files (destructive — explicit flag required)
python -m ao_classifier ./my_tender_folder --mode move --provider gemini
```

---

## LLM backends

| Backend | Privacy | Requirement |
|---|---|---|
| **Ollama (local)** | 100% local, no data sent | `ollama serve` + `ollama pull qwen2.5-coder:7b` |
| **Gemini** | Content sent to Google | `GEMINI_API_KEY` in `.env` or GUI sidebar |
| **Mistral** | Content sent to Mistral | `MISTRAL_API_KEY` in `.env` |

Copy `.env.example` to `.env` and fill in your keys for cloud backends.

### Installing Ollama

```bash
# macOS
brew install ollama
ollama serve
ollama pull qwen2.5-coder:7b

# Windows — download installer from https://ollama.com/download/windows, then:
ollama serve
ollama pull qwen2.5-coder:7b
```

---

## Evaluation workflow

Measure classifier accuracy against a known-good reference folder:

```bash
# 1. Scramble the reference folder (hides structure from the LLM)
python scripts/randomize_folder.py AO24
# → produces AO24_random/ and AO24_mapping.json

# 2. Run the classifier on AO24_random.zip, get ao_plan_TIMESTAMP.json

# 3. Score the result
python scripts/evaluate.py --ref AO24 --plan ao_plan_TIMESTAMP.json --mapping AO24_mapping.json
```

---

## Screenshot

> *Demo screenshot — add one here after a test run.*

---

## License

[MIT](LICENSE)
