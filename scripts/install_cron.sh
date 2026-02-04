#!/bin/bash
# Script pour installer le cron job de synchronisation des contacts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CRON_LOG="/var/log/contacts_sync.log"

# Créer le répertoire de logs si nécessaire
sudo mkdir -p /var/log
sudo touch "$CRON_LOG"
sudo chmod 666 "$CRON_LOG"

# Créer l'entrée cron (utilise le script wrapper qui charge le .env)
CRON_ENTRY="*/5 * * * * $SCRIPT_DIR/scripts/sync_with_env.sh >> $CRON_LOG 2>&1"

# Ajouter au crontab (sans doublons)
(crontab -l 2>/dev/null | grep -v "sync_contacts.py"; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installé avec succès!"
echo "📋 Vérifiez avec: crontab -l"
echo "📝 Logs disponibles dans: $CRON_LOG"
