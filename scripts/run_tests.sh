#!/bin/bash
# Script pour exécuter les tests
# Usage: ./scripts/run_tests.sh [pytest options]

# Aller dans le répertoire du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Variables d'environnement requises pour les tests
export HMAC_SECRET="${HMAC_SECRET:-HMACsecretTest222@@}"
export JWT_SECRET="${JWT_SECRET:-JWTSEcret11@@}"
export PYTHONPATH="${PYTHONPATH:-.}"

echo "🧪 Exécution des tests..."
echo "📍 Répertoire: $SCRIPT_DIR"
echo "🔐 HMAC_SECRET: $HMAC_SECRET"
echo "🔐 JWT_SECRET: $JWT_SECRET"
echo ""

# Exécuter pytest avec les options par défaut si aucune option n'est fournie
if [ $# -eq 0 ]; then
    # Options par défaut: verbose (-v) et afficher les print (-s)
    uv run pytest tests/ -v -s
else
    # Passer toutes les options à pytest
    uv run pytest tests/ "$@"
fi
