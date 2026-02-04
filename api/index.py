"""Handler Vercel pour FastAPI."""
from mangum import Mangum
from app.main import app

# Créer le handler Mangum avec lifespan désactivé
mangum_app = Mangum(app, lifespan="off")

# Exporter comme fonction pour Vercel (signature attendue: event, context)
def handler(event, context):
    """Handler pour Vercel serverless functions."""
    return mangum_app(event, context)
