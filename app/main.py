from fastapi import Depends, FastAPI, HTTPException

from .config import settings  # noqa: F401  # chargé pour valider la config au démarrage
from .odoo_client import OdooClient
from .security import (
    authenticate_user,
    create_access_token,
    get_current_user,
    verify_hmac,
)

app = FastAPI(title="Odoo Contacts API", version="0.1.0")

def get_odoo_client() -> OdooClient:
    return OdooClient()


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
    odoo_client: OdooClient = Depends(get_odoo_client),
):
    try:
        return odoo_client.get_contacts()
    except Exception as exc:  # pragma: no cover - dépend d'Odoo
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/contacts/{contact_id}",
    dependencies=[Depends(verify_hmac)],
)
async def get_contact(
    contact_id: int,
    current_user: str = Depends(get_current_user),  # noqa: ARG001
    odoo_client: OdooClient = Depends(get_odoo_client),
):
    contact = odoo_client.get_contact_by_id(contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

