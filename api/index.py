"""Handler Vercel pour FastAPI."""
from mangum import Mangum
from app.main import app

# Wrapper ASGI pour Vercel
handler = Mangum(app)
