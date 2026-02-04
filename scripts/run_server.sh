#!/bin/bash
# Script pour lancer le serveur FastAPI
# Usage: ./scripts/run_server.sh [--kill] [--port PORT]

PORT=${PORT:-8000}
KILL_EXISTING=false

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --kill)
            KILL_EXISTING=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--kill] [--port PORT]"
            exit 1
            ;;
    esac
done

# Aller dans le répertoire du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Vérifier si le port est déjà utilisé
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Le port $PORT est déjà utilisé!"
        echo ""
        echo "Processus utilisant le port $PORT:"
        lsof -Pi :$PORT -sTCP:LISTEN
        echo ""
        
        if [ "$KILL_EXISTING" = true ]; then
            PID=$(lsof -ti :$PORT)
            if [ -n "$PID" ]; then
                echo "🛑 Arrêt du processus $PID..."
                kill -9 $PID
                sleep 1
                echo "✅ Processus arrêté. Redémarrage du serveur..."
            else
                echo "❌ Impossible de trouver le processus"
                exit 1
            fi
        else
            echo "Options:"
            echo "  1. Arrêter le processus existant (tuer le processus)"
            echo "  2. Utiliser un autre port (ex: PORT=8001 ./scripts/run_server.sh)"
            echo "  3. Utiliser --kill pour arrêter automatiquement (ex: ./scripts/run_server.sh --kill)"
            echo "  4. Quitter"
            echo ""
            read -p "Votre choix (1/2/3/4): " choice
            
            case $choice in
                1)
                    PID=$(lsof -ti :$PORT)
                    if [ -n "$PID" ]; then
                        echo "🛑 Arrêt du processus $PID..."
                        kill -9 $PID
                        sleep 1
                        echo "✅ Processus arrêté. Redémarrage du serveur..."
                    else
                        echo "❌ Impossible de trouver le processus"
                        exit 1
                    fi
                    ;;
                2)
                    read -p "Entrez le nouveau port (défaut: 8001): " new_port
                    PORT=${new_port:-8001}
                    echo "🌐 Utilisation du port $PORT"
                    ;;
                3)
                    PID=$(lsof -ti :$PORT)
                    if [ -n "$PID" ]; then
                        echo "🛑 Arrêt du processus $PID..."
                        kill -9 $PID
                        sleep 1
                        echo "✅ Processus arrêté. Redémarrage du serveur..."
                    else
                        echo "❌ Impossible de trouver le processus"
                        exit 1
                    fi
                    ;;
                4)
                    echo "👋 Au revoir!"
                    exit 0
                    ;;
                *)
                    echo "❌ Choix invalide"
                    exit 1
                    ;;
            esac
        fi
    fi
}

check_port

echo "🚀 Démarrage du serveur FastAPI..."
echo "📍 Répertoire: $SCRIPT_DIR"
echo "🌐 L'API sera accessible sur: http://localhost:$PORT"
echo "📚 Documentation: http://localhost:$PORT/docs"
echo ""

# Lancer le serveur avec uvicorn
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
