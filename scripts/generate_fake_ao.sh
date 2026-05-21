#!/bin/bash
# Génère un faux dossier AO désorganisé pour tester ao_classifier
# Usage : bash generate_fake_ao.sh [dossier_sortie]

OUT="${1:-fake_ao_test}"
mkdir -p "$OUT"

echo "📁 Génération du faux dossier AO dans : $OUT"

# --- Utilitaire : crée un faux PDF lisible (texte brut encodé en PDF minimal)
make_pdf() {
  local path="$1"
  local content="$2"
  mkdir -p "$(dirname "$path")"
  # PDF minimal valide avec texte visible
  python3 - <<PYEOF
import struct, zlib

content = b"""$content"""

# PDF minimal sans lib externe
pdf = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length ${#content}>>
stream
BT /F1 12 Tf 50 750 Td (""" + content + b""") Tj ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
xref
0 6
0000000000 65535 f 
trailer<</Size 6/Root 1 0 R>>
startxref
9
%%EOF"""

with open("$path", "wb") as f:
    f.write(pdf)
PYEOF
  # Fallback : fichier texte si python échoue
  if [ ! -f "$path" ]; then
    echo "$content" > "$path"
  fi
}

# --- Utilitaire : crée un faux fichier texte avec contenu métier
make_txt() {
  local path="$1"
  local content="$2"
  mkdir -p "$(dirname "$path")"
  echo "$content" > "$path"
}

# === FICHIERS DÉSORGANISÉS À LA RACINE ===

make_txt "$OUT/Document1.pdf" "CAHIER DES CLAUSES TECHNIQUES PARTICULIERES
Marché de travaux - Lot 01 Gros Oeuvre
Opération : Construction d'un immeuble de logements collectifs
Maître d'ouvrage : Commune de Marly-le-Roi (78)
Le présent CCTP définit les prescriptions techniques applicables aux travaux de gros oeuvre."

make_txt "$OUT/scan0042.pdf" "ACTE D'ENGAGEMENT
Lot 02 - Charpente Couverture Etanchéité
Je soussigné, représentant de SMA BTP, m'engage à réaliser les travaux décrits
au prix forfaitaire toutes taxes comprises.
Montant HT : 245 000 EUR
Validité de l'offre : 120 jours"

make_txt "$OUT/Nouveau document.pdf" "REGLEMENT DE CONSULTATION
Procédure : Appel d'offres ouvert
Objet : Travaux de construction d'une école primaire
Commune de Herblay-sur-Seine (95)
Date limite de remise des offres : 15/03/2025 à 12h00
Critères de jugement : Prix 60% / Valeur technique 40%"

make_txt "$OUT/copie finale v3.docx" "RAPPORT INITIAL DE CONTROLE TECHNIQUE
RICT - Phase PRO
Opération : Résidence Les Acacias - Marly-le-Roi
Bureau de contrôle : SOCOTEC
Indice sismique : Zone 1
Classe d'exposition : XC2"

make_txt "$OUT/CCAP lot 3.pdf" "CAHIER DES CLAUSES ADMINISTRATIVES PARTICULIERES
Lot 03 - Plomberie Sanitaires
Délai d'exécution : 8 mois
Modalités de règlement : Acomptes mensuels sur situations de travaux
Retenue de garantie : 5%
Assurance décennale obligatoire"

make_txt "$OUT/image001.pdf" "DC2 - Déclaration du candidat individuel
Identification du candidat : SMA BTP
SIREN : 775 688 732
Forme juridique : Société anonyme
Chiffre d'affaires HT N-1 : 1 245 000 000 EUR
Effectif moyen annuel : 1 850 salariés"

make_txt "$OUT/questions reponses.pdf" "QUESTIONS - REPONSES N°2
Consultation : Construction école primaire Herblay
Q1 : Les fondations sur pieux sont-elles incluses dans le lot Gros Oeuvre ?
R1 : Oui, les fondations spéciales sont à la charge du lot 01.
Q2 : Le DPGF doit-il être remis signé ?
R2 : Oui, le DPGF signé est une pièce obligatoire de l'offre."

make_txt "$OUT/Attestation 2024.pdf" "ATTESTATION DE RÉGULARITÉ FISCALE
Délivrée par la Direction Générale des Finances Publiques
Au profit de : SMA BTP - SIREN 775 688 732
Valable jusqu'au : 31/12/2024
L'entreprise est à jour de ses obligations fiscales."

make_txt "$OUT/plan masse.pdf" "PLAN DE MASSE
Echelle 1/500
Opération : Construction résidence Herblay-sur-Seine
Architecte : Cabinet DURAND & Associés
Indice : C - Date : janvier 2025
Surface terrain : 2 450 m2 - SHON : 1 820 m2"

make_txt "$OUT/urssaf.pdf" "ATTESTATION DE VIGILANCE
Délivrée par l'URSSAF Ile-de-France
Entreprise : SMA BTP
Période : 4ème trimestre 2024
L'entreprise est à jour de ses cotisations sociales.
Document valable 6 mois à compter de sa date d'émission."

make_txt "$OUT/Extrait KBIS.pdf" "EXTRAIT KBIS
Registre du Commerce et des Sociétés de Paris
Dénomination : SMA BTP
Siège social : 214 boulevard Saint-Germain - 75007 Paris
Capital social : 229 090 160 EUR
Date d'immatriculation : 12/04/1907"

make_txt "$OUT/planning.xlsx" "Planning TCE - Résidence Les Acacias
Tâche | Début | Fin | Durée
Installation chantier | 01/03/2025 | 15/03/2025 | 15j
Gros oeuvre RDC | 16/03/2025 | 30/06/2025 | 106j
Gros oeuvre R+1 | 01/07/2025 | 30/09/2025 | 91j
Charpente couverture | 01/10/2025 | 30/11/2025 | 60j
Second oeuvre | 01/12/2025 | 30/04/2026 | 150j"

make_txt "$OUT/PGCSPS_v2_final.pdf" "PLAN GENERAL DE COORDINATION SPS
Opération : Construction immeuble logements - Herblay
Coordonnateur SPS : Cabinet SPS Consulting
Phase : PRO/EXE
Effectif maximal prévisible : 45 compagnons
Durée des travaux : 18 mois"

make_txt "$OUT/Rapport amiante - bat A.pdf" "RAPPORT DE DIAGNOSTIC AMIANTE AVANT TRAVAUX (DAT)
Bâtiment A - Résidence Les Tilleuls
Donneur d'ordre : SMA BTP
Opérateur de repérage : DEKRA Industrial
Matériaux contenant de l'amiante détectés :
- Dalles de sol vinyle (couche adhésive) : présence confirmée
- Flocage des poutres en béton : absence confirmée"

make_txt "$OUT/etude sol G2 PRO.pdf" "ETUDE GEOTECHNIQUE DE PROJET (G2 PRO)
Site : Rue des Lilas - Herblay-sur-Seine (95)
Maître d'ouvrage : Commune de Herblay
Géotechnicien : GEOTECH Ile-de-France
Contrainte admissible des sols : 180 kPa à 1.50m de profondeur
Fondations recommandées : semelles filantes - ancrage 1.80m / TN"

make_txt "$OUT/convention DO.pdf" "CONVENTION D'ASSURANCE DOMMAGES-OUVRAGE
Souscripteur : Commune de Marly-le-Roi
Assureur : SMA BTP
Opération : Construction immeuble 24 logements
Valeur déclarée à l'achèvement : 4 200 000 EUR HT
Franchise contractuelle : 3 000 EUR
Durée de garantie : 10 ans à compter de la réception"

make_txt "$OUT/AE TRC signé.pdf" "ACTE D'ENGAGEMENT - TOUS RISQUES CHANTIER
Souscripteur : Commune d'Herblay-sur-Seine
Assureur : SMA BTP
Montant des travaux assurés : 6 800 000 EUR HT
Durée de chantier : 20 mois
Date de début prévisionnelle : 01/03/2025
Signé le : 14/02/2025 - Cachet et signature SMA BTP"

make_txt "$OUT/Fiche SOCABAT.doc" "ETUDE DE RISQUE SOCABAT
Référence dossier : AO25-0142
Opération : Construction école primaire - Herblay
Maître d'ouvrage public : Commune de Herblay-sur-Seine
Maître d'oeuvre : Agence ARCHITECTURA
Montant travaux TCE : 5 200 000 EUR HT
Indice risque global : B2 - Risque modéré
Observations : Terrain en légère pente, voisinage sensible côté Nord"

make_txt "$OUT/DC1 pouvoir.pdf" "DC1 - LETTRE DE CANDIDATURE
Identification du candidat : SMA BTP
Représenté par : M. Jean-Pierre MARTIN, Directeur Général Délégué
Pouvoir joint : Oui
Marchés publics pour lesquels la candidature est déposée :
Construction d'une école primaire - Commune de Herblay-sur-Seine
Date et signature : Paris, le 10/02/2025"

make_txt "$OUT/NoticeAccessibilite.pdf" "NOTICE D'ACCESSIBILITE PMR
Opération : Construction résidence 24 logements
Maître d'oeuvre : Cabinet DURAND & Associés
Référentiel : Arrêté du 24 décembre 2015
Ascenseur : obligatoire (R+3)
Logements adaptables : 100% des logements
Cheminement extérieur accessible : conforme"

make_txt "$OUT/archive DCE reçu.zip" "FAKE_ZIP_CONTENT - Dossier de consultation"

make_txt "$OUT/Memoire_technique_v1_FINAL_vf.pdf" "MEMOIRE TECHNIQUE DE GESTION
SMA BTP - Assurance Construction
Organisation de la gestion des sinistres :
Notre dispositif repose sur 3 niveaux d'intervention...
Délai moyen de traitement : 45 jours
Réseau d'experts agréés : 320 experts sur toute la France
Certification ISO 9001 : oui, depuis 2008"

make_txt "$OUT/Pouvoir_signature_Martin.pdf" "DELEGATION DE POUVOIR
SMA BTP - Société anonyme au capital de 229 090 160 EUR
M. Jean-Pierre MARTIN est habilité à signer tout acte d'engagement
dans le cadre des marchés publics d'assurance construction,
sans limitation de montant.
Fait à Paris le 01/01/2025 - Le Président Directeur Général"

make_txt "$OUT/Copie_permis_construire_PC025.pdf" "ARRETE DE PERMIS DE CONSTRUIRE
Commune de Herblay-sur-Seine - Service Urbanisme
N° de dossier : PC 095 306 24 W 0042
Pétitionnaire : SCI Les Lilas
Objet : Construction d'un groupe scolaire 12 classes
Délivré le : 20/09/2024
Le Maire de Herblay-sur-Seine"

# === SOUS-DOSSIERS PARTIELS ET MAL NOMMÉS ===

mkdir -p "$OUT/Divers"
make_txt "$OUT/Divers/RIB_SMABTP_2024.pdf" "RELEVE D'IDENTITE BANCAIRE
Titulaire : SMA BTP
Banque : Crédit Agricole CIB
IBAN : FR76 1820 6004 4132 4567 8901 234
BIC : AGRIFRPP882
Domiciliation : Crédit Agricole CIB - Paris"

make_txt "$OUT/Divers/Extrait_Banque_France.pdf" "AVIS DE LA BANQUE DE FRANCE
Cotation APCR : 3+ (capacité de remboursement satisfaisante)
Entreprise : SMA BTP - SIREN 775 688 732
Date d'émission : 15/01/2025
Document confidentiel - Usage exclusif marchés publics"

make_txt "$OUT/Divers/CCTP lot 4 electricite.pdf" "CAHIER DES CLAUSES TECHNIQUES PARTICULIERES
Lot 04 - Electricité Courants Forts et Faibles
Norme applicable : NF C 15-100
Puissance souscrite prévisionnelle : 3 x 400A
Eclairage secours : BAES autonomes
GTL par logement obligatoire"

mkdir -p "$OUT/Plans architecte"
make_txt "$OUT/Plans architecte/Plan_RDC_indA.pdf" "PLAN ARCHITECTURAL RDC
Echelle 1/100 - Indice A
Opération : Résidence Les Acacias - Marly-le-Roi
Architecte : Cabinet DURAND & Associés
Surface RDC : 412 m2 SHON
Hall d'entrée + local vélos + local poubelles + 4 logements"

make_txt "$OUT/Plans architecte/coupe AA.pdf" "COUPE AA - LONGITUDINALE
Echelle 1/100
Hauteur sous plafond : 2.50m (RDC) / 2.50m (étages courants)
Hauteur totale bâtiment : 14.20m / TN
Acrotère : 0.60m"

make_txt "$OUT/Plans architecte/facade_nord.pdf" "ELEVATION FACADE NORD
Echelle 1/100 - Indice B
Matériaux : Enduit gratté blanc, menuiseries aluminium gris anthracite
Occultations : Volets roulants électriques
Bardage bois : Pin douglas traité classe 4"

mkdir -p "$OUT/Contrat MOE"
make_txt "$OUT/Contrat MOE/AE_MOE_signe.pdf" "ACTE D'ENGAGEMENT MAITRISE D'OEUVRE
Maître d'ouvrage : Commune de Marly-le-Roi
Maître d'oeuvre : Cabinet DURAND & Associés SARL
Mission complète : DIAG/PRO/DCE/ACT/DET/AOR
Taux d'honoraires : 9.2% du montant HT des travaux
Signé le 05/11/2024"

make_txt "$OUT/Contrat MOE/CCAP_MOE.pdf" "CAHIER DES CLAUSES ADMINISTRATIVES PARTICULIERES
Contrat de maîtrise d'oeuvre
Délai de mission : 36 mois à compter de l'ordre de service
Assurance RC professionnelle obligatoire : minimum 2 000 000 EUR
Sous-traitance : soumise à accord préalable du maître d'ouvrage"

mkdir -p "$OUT/old"
make_txt "$OUT/old/AE_v1_obsolete.pdf" "ACTE D'ENGAGEMENT VERSION 1 - OBSOLETE
NE PAS UTILISER - Remplacé par AE lot 02 version finale
Montant initial : 230 000 EUR HT (révisé à 245 000)"

make_txt "$OUT/old/questions v1.pdf" "QUESTIONS REPONSES N°1 - SUPERSEDE PAR VERSION 2
Q1 : Quelles sont les assurances obligatoires ?
R1 : RC décennale, dommages aux existants, TRC."

# Doublons intentionnels (même contenu)
cp "$OUT/urssaf.pdf" "$OUT/URSSAF_attestation_copie.pdf"
cp "$OUT/Extrait KBIS.pdf" "$OUT/Divers/KBIS_copie_backup.pdf"

echo ""
echo "✅ Dossier de test généré : $OUT/"
echo ""
echo "Contenu :"
find "$OUT" -type f | sort | sed 's|^|  |'
echo ""
echo "$(find "$OUT" -type f | wc -l) fichiers au total"
echo ""
echo "Pour tester ao_classifier :"
echo "  python -m ao_classifier ./$OUT --mode dry-run"
