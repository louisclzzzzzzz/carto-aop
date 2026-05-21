"""Vérification des pièces obligatoires par rapport aux documents classifiés."""

import unicodedata
from dataclasses import dataclass, field


def _norm(text: str) -> str:
    """Minuscules + suppression des accents pour comparaison tolérante."""
    return unicodedata.normalize("NFD", text.lower()).encode("ascii", "ignore").decode()


@dataclass
class PieceRequise:
    label: str
    phase: str
    folder_patterns: list[str] = field(default_factory=list)  # sous-chaînes de target_folder
    keyword_patterns: list[str] = field(default_factory=list)  # sous-chaînes de suggested_name/reasoning
    obligatoire: bool = True


# Mapping complet basé sur liste_pieces.md + taxonomie ARBO_TEMPLATE
PIECES_REQUISES: list[PieceRequise] = [
    # ── Phase 1 : Constitution du dossier ──────────────────────────────────
    PieceRequise(
        label="Demande d'assurance SMABTP",
        phase="Constitution du dossier",
        folder_patterns=["ass"],
        keyword_patterns=["assurance", "smabtp", "souscription", "demande assurance", "police"],
    ),
    PieceRequise(
        label="Extrait K-BIS (< 3 mois)",
        phase="Constitution du dossier",
        folder_patterns=["candidature", "kbis"],
        keyword_patterns=["kbis", "k-bis", "extrait k", "registre du commerce"],
    ),
    PieceRequise(
        label="Pièce(s) d'identité des bénéficiaires effectifs",
        phase="Constitution du dossier",
        folder_patterns=[],
        keyword_patterns=["identit", "cni", "passeport", "beneficiaire effectif", "beneficiaires effectifs"],
    ),
    PieceRequise(
        label="CCTP / devis descriptif des entreprises",
        phase="Constitution du dossier",
        folder_patterns=["cctp", "cctp plans", "cctp travaux"],
        keyword_patterns=["cctp", "cahier des clauses techniques", "devis descriptif"],
    ),
    PieceRequise(
        label="Plans (Masse / Façade / Coupe)",
        phase="Constitution du dossier",
        folder_patterns=["tech/plans", "cctp plans"],
        keyword_patterns=["plan masse", "plan facade", "plan coupe", "plans architecte", "plans bet"],
    ),
    PieceRequise(
        label="Planning des travaux",
        phase="Constitution du dossier",
        folder_patterns=["planning"],
        keyword_patterns=["planning", "calendrier previsionnel", "calendrier travaux"],
    ),
    PieceRequise(
        label="Rapport géotechnique G2 PRO",
        phase="Constitution du dossier",
        folder_patterns=["etudes sol", "etude de sol", "g2pro"],
        keyword_patterns=["g2 pro", "g2pro", "geotechnique", "etude de sol", "geotechni"],
    ),
    PieceRequise(
        label="Rapport Initial du Contrôleur Technique",
        phase="Constitution du dossier",
        folder_patterns=["rict", "tech/ct"],
        keyword_patterns=["rapport initial", "rict", "ict", "controleur technique initial"],
    ),
    PieceRequise(
        label="Liste des matériaux de réemploi",
        phase="Constitution du dossier",
        folder_patterns=[],
        keyword_patterns=["reemploi", "reutilisation", "materiaux de reemploi"],
        obligatoire=False,
    ),

    # ── Phase 2 : Établissement du contrat ─────────────────────────────────
    PieceRequise(
        label="Copie DOC signée (ou 1er OS)",
        phase="Établissement du contrat",
        folder_patterns=[],
        keyword_patterns=["declaration d ouverture", "ouverture de chantier", "doc signe", "ordre de service", " doc "],
    ),
    PieceRequise(
        label="Arrêté du Permis de Construire (ou déclaration de travaux)",
        phase="Établissement du contrat",
        folder_patterns=["arrete pc"],
        keyword_patterns=["permis de construire", "arrete pc", "declaration de travaux", "arrete permis"],
    ),
    PieceRequise(
        label="Contrat(s) de Maîtrise d'Œuvre",
        phase="Établissement du contrat",
        folder_patterns=["contrats moe", "contrat moe"],
        keyword_patterns=["contrat moe", "contrat de maitrise d oeuvre", "marche moe"],
    ),
    PieceRequise(
        label="Liste de tous les intervenants",
        phase="Établissement du contrat",
        folder_patterns=["liste intervenants"],
        keyword_patterns=["liste des intervenants", "liste intervenants", "intervenants chantier"],
    ),
    PieceRequise(
        label="Attestations d'assurance décennale de tous les intervenants",
        phase="Établissement du contrat",
        folder_patterns=["att ass"],
        keyword_patterns=["decennale", "assurance decennale", "attestation assurance", "attestation decennale"],
    ),
    PieceRequise(
        label="Référé Préventif (si avoisinant)",
        phase="Établissement du contrat",
        folder_patterns=[],
        keyword_patterns=["refere preventif", "refere", "preventif", "avoisinant"],
        obligatoire=False,
    ),

    # ── Phase 3 : Réception du chantier ────────────────────────────────────
    PieceRequise(
        label="PV de réception (avec levée des réserves)",
        phase="Réception du chantier",
        folder_patterns=[],
        keyword_patterns=["pv de reception", "proces-verbal de reception", "reception chantier", "levee des reserves"],
    ),
    PieceRequise(
        label="Déclaration du coût définitif",
        phase="Réception du chantier",
        folder_patterns=["droc"],
        keyword_patterns=["cout definitif", "declaration du cout", "dreo", "droc", "cout final"],
    ),
    PieceRequise(
        label="Rapport Final du Contrôleur Technique",
        phase="Réception du chantier",
        folder_patterns=["rict"],
        keyword_patterns=["rapport final", "rfc", "controleur technique final", "rapport de fin"],
    ),
]


@dataclass
class ChecklistResult:
    piece: PieceRequise
    found: bool
    matching_files: list[str]  # suggested_name des fichiers qui matchent


def _entry_matches(entry_folder: str, entry_name: str, entry_reasoning: str, piece: PieceRequise) -> bool:
    folder_n = _norm(entry_folder)
    name_n = _norm(entry_name)
    reasoning_n = _norm(entry_reasoning or "")
    haystack = f"{folder_n} {name_n} {reasoning_n}"

    for pat in piece.folder_patterns:
        if _norm(pat) in folder_n:
            return True
    for pat in piece.keyword_patterns:
        if _norm(pat) in haystack:
            return True
    return False


def build_checklist(entries: list) -> list[ChecklistResult]:
    """Construit la checklist en cherchant chaque pièce dans les entrées classifiées."""
    results: list[ChecklistResult] = []
    for piece in PIECES_REQUISES:
        matching: list[str] = []
        for e in entries:
            folder = getattr(e, "target_folder", "") or ""
            name = getattr(e, "suggested_name", "") or ""
            reasoning = getattr(e, "reasoning", "") or ""
            if _entry_matches(folder, name, reasoning, piece):
                matching.append(name)
        results.append(ChecklistResult(piece=piece, found=bool(matching), matching_files=matching))
    return results
