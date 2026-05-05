"""Interface graphique Streamlit : dépose un ZIP, lance l'analyse, affiche le listing."""

import io
import logging
import shutil
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

# Permet d'exécuter via `streamlit run ao_classifier/gui.py` (le parent n'est
# pas dans sys.path par défaut quand Streamlit lance le fichier comme script).
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd
import streamlit as st

from ao_classifier.classifier import check_ollama, classify_all
from ao_classifier.config import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_MODEL,
    OLLAMA_BASE_URL,
)
from ao_classifier.extractor import enrich_files
from ao_classifier.planner import build_plan
from ao_classifier.scanner import scan

logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="AO Classifier",
    page_icon="📁",
    layout="wide",
)


def extract_zip(uploaded_file, dest: Path) -> Path:
    """Décompresse le ZIP dans dest et retourne le dossier racine extrait."""
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as zf:
        zf.extractall(dest)

    # Si un seul dossier au premier niveau, on l'utilise comme racine
    children = [p for p in dest.iterdir() if p.is_dir()]
    if len(children) == 1 and not any(p.is_file() for p in dest.iterdir()):
        return children[0]
    return dest


def run_pipeline(input_folder: Path, model: str, batch_size: int, threshold: float):
    """Exécute le pipeline complet et retourne (entries, output_root)."""
    output_root = input_folder.parent / f"{input_folder.name}_organized"

    files = scan(input_folder)
    if not files:
        return [], output_root

    files = enrich_files(files)

    results = classify_all(
        files,
        model=model,
        base_url=OLLAMA_BASE_URL,
        batch_size=batch_size,
        confidence_threshold=threshold,
    )

    entries = build_plan(results, output_root, threshold)
    return entries, output_root


def build_dataframe(entries) -> pd.DataFrame:
    rows = []
    for e in entries:
        rows.append({
            "Fichier source": str(e.original_path),
            "Dossier cible": e.target_folder,
            "Nouveau nom": e.suggested_name,
            "Confiance": e.confidence,
            "Action": e.action,
            "Raison": e.reasoning,
        })
    df = pd.DataFrame(rows)
    return df


def build_tree(entries) -> str:
    """Représentation arborescence ASCII du dossier réorganisé."""
    by_folder: dict[str, list[str]] = {}
    for e in entries:
        by_folder.setdefault(e.target_folder, []).append(e.suggested_name)

    lines = ["<dossier_organized>/"]
    folders = sorted(by_folder.keys())
    for i, folder in enumerate(folders):
        is_last_folder = i == len(folders) - 1
        prefix = "└── " if is_last_folder else "├── "
        lines.append(f"{prefix}{folder}/")
        files = sorted(by_folder[folder])
        for j, name in enumerate(files):
            is_last_file = j == len(files) - 1
            sub = "    " if is_last_folder else "│   "
            file_prefix = "└── " if is_last_file else "├── "
            lines.append(f"{sub}{file_prefix}{name}")
    return "\n".join(lines)


# ─── UI ──────────────────────────────────────────────────────────────────────

st.title("📁 AO Classifier")
st.caption("Dépose un dossier ZIP d'appel d'offres, l'IA propose la réorganisation.")

with st.sidebar:
    st.header("Paramètres")
    model = st.selectbox(
        "Modèle Ollama",
        ["qwen2.5-coder:7b", "qwen2.5:7b", "mistral:7b", "llama3.2:3b"],
        index=0,
    )
    batch_size = st.slider("Taille de batch", 1, 10, DEFAULT_BATCH_SIZE)
    threshold = st.slider(
        "Seuil de confiance",
        0.0, 1.0, DEFAULT_CONFIDENCE_THRESHOLD, 0.05,
    )

    st.divider()
    if check_ollama(OLLAMA_BASE_URL):
        st.success("✓ Ollama accessible")
    else:
        st.error("✗ Ollama injoignable\n\n`ollama serve`")

uploaded = st.file_uploader(
    "Glisse-dépose un ZIP",
    type=["zip"],
    help="Le contenu sera analysé localement, rien n'est envoyé sur internet.",
)

if uploaded is None:
    st.info("👆 Dépose un fichier ZIP pour démarrer.")
    st.stop()

st.write(f"**Fichier reçu :** `{uploaded.name}` ({uploaded.size / 1024:.1f} Ko)")

if not st.button("🚀 Lancer l'analyse", type="primary"):
    st.stop()

with tempfile.TemporaryDirectory(prefix="ao_gui_") as tmp:
    tmp_path = Path(tmp)
    extract_dir = tmp_path / "extracted"

    with st.spinner("Décompression du ZIP..."):
        input_folder = extract_zip(uploaded, extract_dir)

    progress = st.empty()
    progress.info(f"📂 Dossier extrait : `{input_folder.name}`")

    with st.spinner(
        "Analyse en cours… scan + extraction + classement LLM "
        "(peut prendre plusieurs minutes selon le modèle)"
    ):
        try:
            entries, output_root = run_pipeline(
                input_folder, model, batch_size, threshold,
            )
        except Exception as exc:
            st.error(f"Erreur pendant l'analyse : {exc}")
            logger.exception("Pipeline failed")
            st.stop()

    progress.empty()

    if not entries:
        st.warning("Aucun fichier exploitable trouvé dans le ZIP.")
        st.stop()

    # ─── Métriques ──────────────────────────────────────────────────────────
    total = len(entries)
    confident = sum(1 for e in entries if e.confidence >= threshold and e.action == "copy")
    review = sum(1 for e in entries if e.action == "manual_review")
    duplicates = sum(1 for e in entries if e.action == "duplicate")
    avg_conf = sum(e.confidence for e in entries) / total if total else 0

    st.success(f"✅ Analyse terminée — {total} fichier(s) traité(s)")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total fichiers", total)
    c2.metric("Bien classés", confident, f"{confident/total*100:.0f}%")
    c3.metric("À réviser", review, delta=f"-{review}" if review else None, delta_color="inverse")
    c4.metric("Doublons", duplicates)
    c5.metric("Confiance moyenne", f"{avg_conf*100:.0f}%")

    # ─── Listing principal : tableau ────────────────────────────────────────
    st.subheader("📋 Listing des classements")
    df = build_dataframe(entries)
    df_sorted = df.sort_values(["Dossier cible", "Confiance"], ascending=[True, False])

    st.dataframe(
        df_sorted,
        column_config={
            "Confiance": st.column_config.ProgressColumn(
                "Confiance",
                format="%.0f%%",
                min_value=0,
                max_value=1,
            ),
            "Action": st.column_config.TextColumn("Action"),
            "Raison": st.column_config.TextColumn("Raison", width="large"),
        },
        hide_index=True,
        use_container_width=True,
        height=520,
    )

    # ─── Répartition par dossier ────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📊 Répartition par dossier cible")
        counts = Counter(e.target_folder for e in entries)
        chart_df = pd.DataFrame(
            sorted(counts.items(), key=lambda x: -x[1]),
            columns=["Dossier", "Nombre"],
        )
        st.bar_chart(chart_df.set_index("Dossier"))

    with col_right:
        st.subheader("🌳 Arborescence proposée")
        st.code(build_tree(entries), language="text")

    # ─── Alertes ────────────────────────────────────────────────────────────
    if review:
        st.subheader("⚠️ À réviser manuellement")
        df_review = df[df["Action"] == "manual_review"][
            ["Fichier source", "Dossier cible", "Nouveau nom", "Confiance", "Raison"]
        ]
        st.dataframe(df_review, hide_index=True, use_container_width=True)

    if duplicates:
        st.subheader("🗑️ Doublons détectés")
        df_dup = df[df["Action"] == "duplicate"][
            ["Fichier source", "Raison"]
        ]
        st.dataframe(df_dup, hide_index=True, use_container_width=True)

    # ─── Export ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("💾 Export")
    csv = df_sorted.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger le listing (CSV)",
        csv,
        file_name=f"ao_listing_{uploaded.name.replace('.zip', '')}.csv",
        mime="text/csv",
    )

    import json
    plan_dict = [
        {
            "source": str(e.original_path),
            "target_folder": e.target_folder,
            "suggested_name": e.suggested_name,
            "action": e.action,
            "confidence": e.confidence,
            "reasoning": e.reasoning,
        }
        for e in entries
    ]
    st.download_button(
        "Télécharger le plan (JSON)",
        json.dumps(plan_dict, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"ao_plan_{uploaded.name.replace('.zip', '')}.json",
        mime="application/json",
    )
