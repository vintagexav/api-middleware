#!/bin/bash
# Script wrapper pour synchroniser les contacts en chargeant le .env

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Charger les variables d'environnement depuis .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Exécuter le script de synchronisation
/usr/local/bin/uv run python sync_contacts.py
