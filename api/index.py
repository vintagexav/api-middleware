"""Handler Vercel pour FastAPI avec Mangum."""
from mangum import Mangum
from app.main import app

# Utiliser lifespan="off" pour éviter les problèmes avec Vercel
# et exporter directement l'objet Mangum
handler = Mangum(app, lifespan="off")
