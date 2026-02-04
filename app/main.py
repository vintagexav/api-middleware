from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .config import settings  # noqa: F401  # chargé pour valider la config au démarrage
from .database import get_db
from .db_client import DBClient
from .security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_hmac,
)

app = FastAPI(title="Odoo Contacts API", version="0.1.0")


@app.post("/auth/login")
async def login(username: str = Depends(authenticate_user)):
    access_token = create_access_token(subject=username)
    return {"access_token": access_token, "token_type": "bearer"}


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

