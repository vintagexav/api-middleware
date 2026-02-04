#!/bin/bash
# Script pour exécuter uniquement les tests d'intégration
# Usage: ./scripts/run_integration_tests.sh [pytest options]

# Aller dans le répertoire du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Variables d'environnement requises pour les tests
export HMAC_SECRET="${HMAC_SECRET:-HMACsecretTest222@@}"
export JWT_SECRET="${JWT_SECRET:-JWTSEcret11@@}"
export PYTHONPATH="${PYTHONPATH:-.}"

echo "🔗 Exécution des tests d'intégration..."
echo "📍 Répertoire: $SCRIPT_DIR"
echo "🔐 HMAC_SECRET: $HMAC_SECRET"
echo "🔐 JWT_SECRET: $JWT_SECRET"
echo ""
echo "⚠️  Note: Les tests d'intégration nécessitent une connexion active à Odoo."
echo "   Assurez-vous que les variables d'environnement suivantes sont configurées :"
echo "   - ODOO_URL"
echo "   - ODOO_DB"
echo "   - ODOO_USER"
echo "   - ODOO_PASSWORD"
echo ""

# Exécuter pytest avec les options par défaut si aucune option n'est fournie
if [ $# -eq 0 ]; then
    # Options par défaut: verbose (-v) et afficher les print (-s)
    uv run pytest tests/integration/ -v -s
else
    # Passer toutes les options à pytest
    uv run pytest tests/integration/ "$@"
fi
