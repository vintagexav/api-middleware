from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .config import settings  # noqa: F401  # chargé pour valider la config au démarrage
from .database import Base, engine, get_db
from .db_client import DBClient
from .odoo_client import OdooClient
from .security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_hmac,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Startup: Créer les tables au démarrage (avec gestion d'erreur)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log l'erreur mais ne bloque pas le démarrage
        # Les tables seront créées à la première requête si nécessaire
        print(f"Warning: Could not create tables at startup: {e}")
    yield
    # Shutdown: Nettoyage si nécessaire


app = FastAPI(title="Odoo Contacts API", version="0.1.0", lifespan=lifespan)


@app.get("/")
async def root():
    """Endpoint de santé pour vérifier que l'API fonctionne."""
    return {
        "status": "ok",
        "message": "Odoo Contacts API is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Endpoint de santé détaillé."""
    from sqlalchemy import text
    
    try:
        # Tester la connexion à la base de données
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status,
        "environment": {
            "has_database_url": bool(getattr(settings, "database_url", None)),
            "has_odoo_config": bool(getattr(settings, "odoo_url", None)),
        }
    }


@app.post("/auth/login")
async def login(username: str = Depends(authenticate_user)):
    access_token = create_access_token(subject=username)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/fetched")
async def get_fetched_contacts():
    """Récupère les contacts directement depuis Odoo."""
    try:
        odoo = OdooClient()
        return odoo.get_contacts()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/contacts",
    dependencies=[Depends(verify_hmac)],
)
async def get_contacts(
    current_user: str = Depends(get_current_user),  # noqa: ARG001
    db: Session = Depends(get_db),
):
    """Récupère tous les contacts depuis la base de données."""
    try:
        db_client = DBClient(db)
        return db_client.get_contacts()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/contacts/{contact_id}",
    dependencies=[Depends(verify_hmac)],
)
async def get_contact(
    contact_id: int,
    current_user: str = Depends(get_current_user),  # noqa: ARG001
    db: Session = Depends(get_db),
):
    """Récupère un contact par ID depuis la base de données."""
    db_client = DBClient(db)
    contact = db_client.get_contact_by_id(contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

