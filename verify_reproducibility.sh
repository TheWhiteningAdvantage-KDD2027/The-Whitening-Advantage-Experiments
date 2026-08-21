#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# CONFIGURATION ET FIXATION DE L'ENVIRONNEMENT DÉTERMINISTE (CONFORME README §3)
# ==============================================================================
export PYTHONHASHSEED=42
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MKL_CBWR=COMPATIBLE
export SOURCE_DATE_EPOCH=1700000000
export LC_ALL=C

REPO_DIR="/home/m53/The-Whitening-Advantage-Experiments"
cd "$REPO_DIR"

echo "=== [ ÉTAPE 1/5 ] Vérification du dépôt et de l'environnement ==="
if [ ! -f "run_all.sh" ]; then
    echo "ERREUR : run_all.sh est introuvable dans $REPO_DIR" >&2
    exit 1
fi
chmod +x run_all.sh

# Nettoyage des artefacts temporaires de test antérieurs
rm -rf results_run1 results_run2 manifest_run1.sha256 manifest_run2.sha256 results_diff.patch

# ==============================================================================
# RUN #1 : RÉGÉNÉRATION ET EMPREINTE INITIALE
# ==============================================================================
echo "=== [ ÉTAPE 2/5 ] Lancement du RUN #1 (Purge + run_all.sh) ==="
find results/ -mindepth 1 -delete

./run_all.sh 2>&1 | tee logs/double_run_1.log

if [ ! -d "results" ] || [ -z "$(ls -A results)" ]; then
    echo "ERREUR : Le dossier results/ est vide après le RUN #1." >&2
    exit 1
fi

echo "Sauvegarde du résultat : results/ -> results_run1/..."
cp -a results results_run1

echo "Génération du manifest SHA-256 (Run #1)..."
(cd results_run1 && find . -type f -exec sha256sum {} + | LC_ALL=C sort -k2) > manifest_run1.sha256
echo "Run #1 terminé : $(wc -l < manifest_run1.sha256) fichiers indexés."

# ==============================================================================
# RUN #2 : PURGE ET SECONDE RÉGÉNÉRATION
# ==============================================================================
echo "=== [ ÉTAPE 3/5 ] Lancement du RUN #2 (Purge + run_all.sh) ==="
find results/ -mindepth 1 -delete

./run_all.sh 2>&1 | tee logs/double_run_2.log

if [ ! -d "results" ] || [ -z "$(ls -A results)" ]; then
    echo "ERREUR : Le dossier results/ est vide après le RUN #2." >&2
    exit 1
fi

echo "Sauvegarde du résultat : results/ -> results_run2/..."
cp -a results results_run2

echo "Génération du manifest SHA-256 (Run #2)..."
(cd results_run2 && find . -type f -exec sha256sum {} + | LC_ALL=C sort -k2) > manifest_run2.sha256
echo "Run #2 terminé : $(wc -l < manifest_run2.sha256) fichiers indexés."

# ==============================================================================
# COMPARISON STRICTE ET VERDICT
# ==============================================================================
echo "=== [ ÉTAPE 4/5 ] Comparaison des deux manifests ==="
if diff -u manifest_run1.sha256 manifest_run2.sha256 > results_diff.patch; then
    echo "======================================================================"
    echo "SUCCÈS ABSOLU : Déterminisme bit à bit vérifié de bout en bout !"
    echo "L'arbre results/ génère des empreintes SHA-256 100% identiques."
    echo "======================================================================"
    rm -rf results_run1 results_run2 manifest_run1.sha256 manifest_run2.sha256 results_diff.patch
    exit 0
else
    echo "======================================================================" >&2
    echo "ÉCHEC : Divergence d'empreintes détectée entre Run #1 et Run #2 !" >&2
    echo "Consultez le fichier de patch : $REPO_DIR/results_diff.patch" >&2
    echo "======================================================================" >&2
    exit 1
fi