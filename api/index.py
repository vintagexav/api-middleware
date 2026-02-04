"""Handler Vercel pour FastAPI."""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from app.main import app

# Wrapper ASGI pour Vercel
# Note: Mangum gère automatiquement le lifespan de FastAPI
handler = Mangum(app)
