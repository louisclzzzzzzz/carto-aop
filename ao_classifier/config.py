"""Constantes, template arborescence cible, glossaire métier."""

from pathlib import Path

# URL Ollama par défaut
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_BATCH_SIZE = 1
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
LLM_TIMEOUT_SECONDS = 30
LLM_MAX_RETRIES = 2
CONTENT_SAMPLE_MAX_CHARS = 1500

# Gemini
GEMINI_DEFAULT_MODEL = "gemini-1.5-flash"
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash-lite",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemma-3-4b-it",
]
OLLAMA_MODELS = [
    "qwen2.5-coder:7b",
    "qwen2.5:7b",
    "mistral:7b",
    "llama3.2:3b",
]

# Fichiers système à ignorer
IGNORED_FILENAMES = {
    "thumbs.db", ".ds_store", "desktop.ini", "ehthumbs.db",
}
IGNORED_PREFIXES = ("~$",)

# Extensions d'archives supportées
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar"}

# Fichiers plateforme dématérialisée → toujours dans depot
DEMAT_EXTENSIONS = {".cle", ".cry", ".xml", ".pli"}

# Template d'arborescence cible (dossier → description)
ARBO_TEMPLATE: dict[str, str] = {
    # ── Racine AO ────────────────────────────────────────────────────────────
    "1.ETUDE BD": "Documents internes SMA (AE interne, annexes, étude de risque)",
    "1.ETUDE BD/LOT XX": "Sous-dossier par lot quand l'étude BD est décomposée (LOT DO, LOT TRC, LOT 1 ET 2…)",
    "2.COPIE DCE": "Archive DCE brute reçue (zip/rar/7z du DCE complet)",
    "2.COPIE DCE/COMPL": "Compléments DCE reçus après dépôt initial",
    "2.COPIE DCE/COMPL/AE TRAVAUX": "Acte d'Engagement travaux reçu en complément",
    "2.COPIE DCE/COMPL/ARRETE PC": "Arrêté PC reçu en complément DCE",
    "2.COPIE DCE/COMPL/ATT ASS/ENT": "Attestations assurance de l'entreprise (complément DCE)",
    "2.COPIE DCE/COMPL/ATT ASS/MOE": "Attestations assurance de la MOE (complément DCE)",
    "2.COPIE DCE/COMPL/G2AVP-PRO": "Étude géotechnique G2 AVP/PRO reçue en complément DCE",
    "2.COPIE DCE/COMPL/LISTE INTERVENANTS": "Liste des intervenants reçue en complément DCE",

    # ── ADMIN ────────────────────────────────────────────────────────────────
    "ADMIN": "Pièces administratives de la consultation",
    "ADMIN/AAPC": "Avis d'Appel Public à la Concurrence",
    "ADMIN/GAN": "Documents Groupama/GAN (assurance DO liée à la consultation)",
    "ADMIN/PF": "Pièces financières (plan de financement, décisions)",
    "ADMIN/RC DCE": "Règlement de la Consultation (version DCE)",
    "ADMIN/RC": "Règlement de la Consultation",
    "ADMIN/CCAP": "Cahier des Clauses Administratives Particulières",
    "ADMIN/CCP": "Cahier des Clauses Particulières",
    "ADMIN/CG CCP CCAP": "CG + CCP + CCAP regroupés (par lot si multi-lots)",

    # ── ASS ──────────────────────────────────────────────────────────────────
    "ASS": "Pièces assurances (polices, marchés signés, attestations)",
    "ASS/ATT ASS": "Attestations d'assurance",
    "ASS/ATT ASS/ENT": "Attestations assurance de l'entreprise",
    "ASS/ATT ASS/MOE": "Attestations assurance de la maîtrise d'œuvre",
    "ASS/CCAP": "CCAP transmis / annoté côté assurance",
    "ASS/CCTP": "CCTP transmis / annoté côté assurance",
    "ASS/GAN": "Documents Groupama/GAN côté assurance",
    "ASS/PF": "Pièces financières côté assurance",
    "ASS/RC": "RC côté assurance",
    "ASS/DEROG COM": "Dérogations de commissionnement assurance",
    "ASS/LISTE INTERVENANTS": "Liste des intervenants (côté assurance)",
    "ASS/MARCHE SIGNE": "Marché(s) signé(s)",

    # ── ENVOI DEMAT ──────────────────────────────────────────────────────────
    "ENVOI DEMAT/CANDIDATURE": "Pièces candidature (DC1, DC2, KBIS, attestations fiscales/sociales)",
    "ENVOI DEMAT/OFFRE": "Pièces offre (AE signé, mémoire technique, DPGF par lot)",
    "ENVOI DEMAT/COPIE DEPOT": "Preuves de dépôt sur la plateforme",
    "ENVOI DEMAT/COPIE DEPOT/CSL_*/COPIE_SAUVEGARDE": "Sauvegarde chiffrée du dépôt (fichiers .cle/.cry/.xml/.pli et offres par lot)",
    "ENVOI DEMAT/depot": "Variante de nommage pour COPIE DEPOT (même contenu)",
    "ENVOI DEMAT/LOT X-Y": "Pièces d'envoi regroupées par tranche de lots",

    # ── QR ───────────────────────────────────────────────────────────────────
    "QR": "Questions/Réponses publiées par le maître d'ouvrage",

    # ── TECH ─────────────────────────────────────────────────────────────────
    "TECH/ARRETE PC": "Arrêté du Permis de Construire",
    "TECH/CCTP": "Cahiers des Clauses Techniques Particulières par lot",
    "TECH/CCTP PLANS": "CCTP et plans regroupés dans un même dossier",
    "TECH/CCTP TRAVAUX": "CCTP travaux (variante de nommage, même nature)",
    "TECH/PLANS": "Plans architecte et BET (PDF et DWG, sous-dossiers par discipline)",
    "TECH/PLANNING": "Planning prévisionnel de chantier",
    "TECH/ETUDES SOL": "Études géotechniques (G1, G2 AVP, G2 PRO, G5)",
    "TECH/ETUDE DE SOL": "Variante de nommage pour ETUDES SOL",
    "TECH/G2PRO": "Étude géotechnique G2 PRO (nommée directement sans dossier ETUDES SOL)",
    "TECH/RICT": "Rapport Initial de Contrôle Technique",
    "TECH/DIAG": "Diagnostics amiante/plomb, PGCSPS, état des risques",
    "TECH/CONTRATS MOE": "Contrats et avenants Maîtrise d'Œuvre (pluriel)",
    "TECH/CONTRAT MOE": "Variante singulier de CONTRATS MOE",
    "TECH/CONV BC": "Convention Bureau de Contrôle",
    "TECH/CT": "Contrat Bureau de Contrôle (variante de nommage de CONV BC)",
    "TECH/CONTRAT CT": "Variante de nommage pour contrat Bureau de Contrôle",
    "TECH/SOCABAT": "Étude de risque SOCABAT",
    "TECH/DROC": "Dossier de Récolement / document spécifique opération",
    "TECH/NOTICE DESCRIPTIVE": "Notice descriptive de l'opération",
    "TECH/NOTICE": "Variante courte de NOTICE DESCRIPTIVE",
    "TECH/PIECES COMPLEMENTAIRES": "Pièces complémentaires techniques (plans et docs additionnels)",
    "TECH/AUTRES PIECES": "Pièces diverses non classées ailleurs (variante de PIECES COMPLEMENTAIRES)",
    "TECH/AUTRES": "Idem — variante courte",
    "TECH/LISTE INTERVENANTS": "Liste des intervenants (côté technique)",
    "TECH/COMPL PIECES": "Compléments de pièces techniques reçus en cours de consultation",

    # ── Dossiers par site (opérations multi-bâtiments) ───────────────────────
    "TECH/CONSERVATOIRE": "Sous-dossier technique dédié au bâtiment Conservatoire",
    "TECH/POLE JEUNESSE": "Sous-dossier technique dédié au bâtiment Pôle Jeunesse",

    # ── Fourre-tout ──────────────────────────────────────────────────────────
    "À TRIER": "Fichiers non identifiés avec certitude — révision manuelle requise",
}

GLOSSAIRE = """
Glossaire métier marchés publics BTP :

── Documents de consultation ──────────────────────────────────────────────────
- DCE   : Dossier de Consultation des Entreprises
- AAPC  : Avis d'Appel Public à la Concurrence
- RC    : Règlement de Consultation
- CCAP  : Cahier des Clauses Administratives Particulières
- CCTP  : Cahier des Clauses Techniques Particulières
- CCP   : Cahier des Clauses Particulières
- CG    : Cahier Général (clauses générales, souvent groupé avec CCP/CCAP)
- AE    : Acte d'Engagement (signé par le soumissionnaire)
- DPGF  : Décomposition du Prix Global et Forfaitaire (tableau de prix à remplir)
- BPU   : Bordereau des Prix Unitaires

── Candidature & dépôt ────────────────────────────────────────────────────────
- DC1 / DC2 : Formulaires officiels de candidature marchés publics
- KBIS  : Extrait registre de commerce (preuve d'identité de l'entreprise)
- PF    : Pièces Financières (plan de financement, décisions budgétaires)
- CSL_* : Identifiant de session de dépôt sur plateforme dématérialisée
- PADES : Format de signature électronique (suffixe _PADES sur les fichiers signés)
- Préfixes fichiers : C. = Candidature, O. = Offre (O.1, O.2… par lot)
- DEMAT : Dématérialisé (envoi / dépôt via plateforme en ligne)
- QR    : Questions / Réponses publiées par le maître d'ouvrage en cours de consultation

── Intervenants ───────────────────────────────────────────────────────────────
- MOE   : Maîtrise d'Œuvre (architecte + BET)
- BET   : Bureau d'Études Techniques
- ENT   : Entreprise soumissionnaire / titulaire du marché
- OPC   : Ordonnancement, Pilotage et Coordination de chantier
- CSPS  : Coordonnateur Sécurité et Protection de la Santé
- CSSI  : Coordonnateur Système de Sécurité Incendie
- BC    : Bureau de Contrôle (organisme de vérification technique)
- CT    : Contrôleur Technique (intervenant Bureau de Contrôle)

── Assurances ─────────────────────────────────────────────────────────────────
- DO    : Dommages-Ouvrage (assurance obligatoire maître d'ouvrage)
- TRC   : Tous Risques Chantier
- RCMOA : Responsabilité Civile Maîtrise d'Œuvre / Architecte
- GAN   : Groupama / GAN (assureur DO fréquent sur les dossiers SMA BTP)
- ATT ASS : Attestation d'Assurance
- DEROG COM : Dérogation de Commissionnement (accord dérogatoire assureur)
- MARCHE SIGNE : Marché finalisé et signé par les deux parties

── Technique & études ─────────────────────────────────────────────────────────
- PC    : Permis de Construire
- ARRETE PC : Arrêté municipal autorisant le Permis de Construire
- RICT  : Rapport Initial de Contrôle Technique
- DROC  : Déclaration d'Ouverture de Chantier (ou Dossier de Récolement selon contexte)
- PGCSPS : Plan Général de Coordination Sécurité et Protection de la Santé
- DAD / DAT : Diagnostics Amiante avant Démolition / avant Travaux
- G1    : Étude géotechnique de faisabilité (phase esquisse)
- G2 AVP : Étude géotechnique avant-projet
- G2 PRO : Étude géotechnique projet (phase PRO)
- G5    : Étude géotechnique de supervision d'exécution
- SOCABAT : Organisme d'études de risque pour assureurs construction
- NOTICE DESCRIPTIVE : Document de présentation technique de l'opération
- CONV BC : Convention liant le maître d'ouvrage au Bureau de Contrôle

── Phases & opération ─────────────────────────────────────────────────────────
- AOP   : Appel d'Offres Public
- BD    : Bordereau / Base de Données interne SMA (étude de risque)
- ETUDE BD : Étude interne SMA BTP préalable à la souscription
- MPGS  : Marché Passé sans mise en concurrence (procédure spécifique)
- ACCORD CADRE : Marché à bons de commande sur plusieurs années
- LOT   : Sous-ensemble d'un marché attribué séparément (LOT 1, LOT TRC…)
"""

ARBO_TEMPLATE_TEXT = "\n".join(
    f"- {dossier} : {desc}" for dossier, desc in ARBO_TEMPLATE.items()
)
