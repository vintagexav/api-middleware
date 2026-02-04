"""Handler Vercel pour FastAPI."""
import os
import sys

# Ajouter le répertoire parent au path pour les imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mangum import Mangum
from app.main import app

# Wrapper ASGI pour Vercel
# Mangum gère automatiquement le lifespan de FastAPI
handler = Mangum(app)
