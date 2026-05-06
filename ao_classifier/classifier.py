"""Classement LLM des fichiers — backends Ollama et Gemini."""

import json
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from ao_classifier.config import (
    ARBO_TEMPLATE_TEXT,
    DEMAT_EXTENSIONS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MODEL,
    GEMINI_DEFAULT_MODEL,
    GLOSSAIRE,
    LLM_MAX_RETRIES,
    LLM_TIMEOUT_SECONDS,
    OLLAMA_BASE_URL,
)
from ao_classifier.scanner import FileInfo

logger = logging.getLogger(__name__)

FALLBACK_FOLDER = "À TRIER"
FALLBACK_CONFIDENCE = 0.1


@dataclass
class ClassificationResult:
    file_info: FileInfo
    target_folder: str
    suggested_name: str
    confidence: float
    reasoning: str


def check_ollama(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Vérifie qu'Ollama est accessible."""
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False


def check_gemini(api_key: str) -> bool:
    """Vérifie que la clef API Gemini est valide."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Appel léger : liste les modèles disponibles
        next(iter(genai.list_models()))
        return True
    except Exception:
        return False


def _call_gemini(prompt: str, model: str, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)
    response = m.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.1),
    )
    return response.text


def _build_prompt(batch: list[FileInfo], arbo_template_text: str | None = None) -> str:
    files_block = ""
    for i, f in enumerate(batch, 1):
        files_block += f"""
--- Fichier {i} ---
Chemin original : {f.relative}
Extension : {f.extension}
Taille : {f.size_bytes} octets
Extrait de contenu :
{f.content_sample or "(aucun contenu extractible)"}
"""
    file_list = ", ".join(f'"{f.relative}"' for f in batch)
    arbo = arbo_template_text or ARBO_TEMPLATE_TEXT
    return f"""Tu es un assistant expert en marchés publics BTP français.
Tu dois classifier EXACTEMENT {len(batch)} fichier(s) dans l'arborescence d'un dossier d'appel d'offres.

{GLOSSAIRE}

Arborescence cible disponible :
{arbo}

Fichiers à classifier ({len(batch)} au total) :
{files_block}

RÈGLES CRITIQUES :
1. Tu DOIS retourner une entrée pour CHACUN des {len(batch)} fichiers listés. Aucun oubli.
2. Utilise EXACTEMENT le chemin original tel qu'il apparaît pour "original_path" : {file_list}
3. Si la confiance < 0.6, utilise "À TRIER" comme target_folder.
4. Pour suggested_name : normalise (pas d'espaces multiples, pas de caractères <>:"/\\|?*), préfixe par type si pertinent (CCTP_, DC1_, AE_, PLAN_, QR_, etc.), conserve l'extension.
5. Réponds UNIQUEMENT avec du JSON valide, rien d'autre.

Format attendu (une entrée par fichier, dans le même ordre) :
{{
  "files": [
    {{
      "original_path": "chemin/exact/du/fichier.pdf",
      "target_folder": "TECH/CCTP",
      "suggested_name": "CCTP_Lot_02_Menuiseries.pdf",
      "confidence": 0.88
    }}
  ]
}}"""


def _clean_json(raw: str) -> str:
    """Extrait le JSON d'une réponse LLM qui peut contenir du texte parasite."""
    raw = raw.strip()
    # Supprimer les blocs ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if match:
        return match.group(1).strip()
    # Trouver le premier { et le dernier }
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return raw[start : end + 1]
    return raw


def _call_ollama(prompt: str, model: str, base_url: str) -> str:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.1,
    }
    r = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=LLM_TIMEOUT_SECONDS,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _classify_batch(
    batch: list[FileInfo],
    model: str,
    base_url: str,
    confidence_threshold: float,
    arbo_template_text: str | None = None,
    provider: str = "ollama",
    gemini_api_key: str | None = None,
) -> list[ClassificationResult]:
    prompt = _build_prompt(batch, arbo_template_text)
    raw = ""

    for attempt in range(1, LLM_MAX_RETRIES + 2):
        try:
            if provider == "gemini":
                raw = _call_gemini(prompt, model, gemini_api_key or "")
            else:
                raw = _call_ollama(prompt, model, base_url)
            break
        except requests.Timeout:
            logger.warning("Timeout LLM (tentative %d/%d)", attempt, LLM_MAX_RETRIES + 1)
            if attempt <= LLM_MAX_RETRIES:
                time.sleep(2 ** attempt)
        except requests.RequestException as e:
            logger.error("Erreur Ollama : %s", e)
            break
        except Exception as e:
            logger.error("Erreur LLM (%s) : %s", provider, e)
            break

    # Parsing JSON — le LLM peut renvoyer {"files": [...]} ou directement [...]
    results: list[ClassificationResult] = []
    try:
        cleaned = _clean_json(raw)
        data = json.loads(cleaned)
        if isinstance(data, list):
            llm_files = data
        elif isinstance(data, dict):
            llm_files = data.get("files", [])
        else:
            llm_files = []
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Réponse LLM non-JSON : %s — classement fallback", e)
        llm_files = []

    # Construire plusieurs index pour un matching tolérant
    # Le LLM peut retourner le chemin complet, juste le nom, ou une variante normalisée
    llm_by_path: dict[str, dict] = {}
    llm_by_name: dict[str, dict] = {}
    llm_by_stem: dict[str, dict] = {}
    for item in llm_files:
        raw_key = str(item.get("original_path", "")).strip()
        norm = raw_key.replace("\\", "/").lower()
        llm_by_path[norm] = item
        # Index par nom de fichier seul
        fname = Path(raw_key).name.lower()
        llm_by_name[fname] = item
        # Index par stem (sans extension) pour les cas de renommage
        stem = Path(raw_key).stem.lower().replace(" ", "_").replace("-", "_")
        llm_by_stem[stem] = item

    def _find_llm_item(file_info: FileInfo) -> dict:
        rel = str(file_info.relative).replace("\\", "/").lower()
        # 1. Chemin relatif exact
        if rel in llm_by_path:
            return llm_by_path[rel]
        # 2. Nom de fichier exact
        fname = file_info.path.name.lower()
        if fname in llm_by_name:
            return llm_by_name[fname]
        # 3. Stem normalisé (espaces/tirets → underscores)
        stem = file_info.path.stem.lower().replace(" ", "_").replace("-", "_")
        if stem in llm_by_stem:
            return llm_by_stem[stem]
        # 4. Chercher si un item du LLM contient le nom du fichier comme sous-chaîne
        for key, item in llm_by_name.items():
            if fname in key or key in fname:
                return item
        return {}

    for file_info in batch:
        # Fichiers plateforme dématérialisée : règle directe
        if file_info.extension in DEMAT_EXTENSIONS:
            results.append(ClassificationResult(
                file_info=file_info,
                target_folder="ENVOI DEMAT/depot",
                suggested_name=file_info.path.name,
                confidence=0.95,
                reasoning="Extension fichier plateforme dématérialisée",
            ))
            continue

        # Chercher la correspondance LLM avec matching tolérant
        item = _find_llm_item(file_info)

        target_folder = item.get("target_folder", FALLBACK_FOLDER)
        confidence = float(item.get("confidence", FALLBACK_CONFIDENCE))
        suggested_name = item.get("suggested_name", file_info.path.name)
        reasoning = item.get("reasoning", "Aucune réponse LLM disponible")

        if confidence < 0.6:
            target_folder = FALLBACK_FOLDER

        results.append(ClassificationResult(
            file_info=file_info,
            target_folder=target_folder,
            suggested_name=suggested_name,
            confidence=confidence,
            reasoning=reasoning,
        ))

    return results


def classify_all(
    files: list[FileInfo],
    model: str = DEFAULT_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    confidence_threshold: float = 0.7,
    provider: str = "ollama",
    gemini_api_key: str | None = None,
) -> list[ClassificationResult]:
    """Classifie tous les fichiers via Ollama ou Gemini par batchs."""
    results: list[ClassificationResult] = []

    # Les doublons ne passent pas par le LLM
    to_classify = [f for f in files if not f.is_duplicate]
    duplicates = [f for f in files if f.is_duplicate]

    for dup in duplicates:
        results.append(ClassificationResult(
            file_info=dup,
            target_folder="DOUBLON",
            suggested_name=dup.path.name,
            confidence=1.0,
            reasoning=f"Doublon de {dup.duplicate_of}",
        ))

    batches = [
        to_classify[i : i + batch_size]
        for i in range(0, len(to_classify), batch_size)
    ]
    total = len(batches)

    for idx, batch in enumerate(batches, 1):
        logger.info(
            "Batch %d/%d — %d fichier(s)",
            idx, total, len(batch),
        )
        batch_results = _classify_batch(
            batch, model, base_url, confidence_threshold,
            provider=provider, gemini_api_key=gemini_api_key,
        )
        results.extend(batch_results)

    return results
