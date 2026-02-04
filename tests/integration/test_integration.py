#!/usr/bin/env python3
"""Tests d'intégration pour vérifier le flux complet Odoo -> API -> Base de données"""

import sys
from pathlib import Path

# Ajouter le répertoire racine du projet au path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.database import Base, get_db
from app.main import app
from app.models import Contact
from app.config import settings
from app.odoo_client import OdooClient


# Créer une base de données temporaire pour les tests
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
temp_db.close()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db.name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables
Base.metadata.create_all(bind=engine)

# Nettoyer le fichier temporaire après les tests
import atexit
atexit.register(lambda: os.unlink(temp_db.name) if os.path.exists(temp_db.name) else None)


# Variable globale pour partager la session entre override_get_db et db_session
_current_db_session = None


def override_get_db():
    """Override de get_db pour utiliser une base de données de test."""
    global _current_db_session
    Base.metadata.create_all(bind=engine)
    # Utiliser la session courante si elle existe
    if _current_db_session is None:
        _current_db_session = TestingSessionLocal()
    try:
        yield _current_db_session
    finally:
        # Ne pas fermer la session ici, elle sera fermée par la fixture
        pass


# Créer le client de test
client = TestClient(app)


@pytest.fixture(autouse=True)
def db_session():
    """Fixture pour créer une session de base de données partagée avec l'API."""
    global _current_db_session
    Base.metadata.create_all(bind=engine)
    _current_db_session = TestingSessionLocal()
    
    # Remplacer la dépendance get_db pour utiliser cette session
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Nettoyer les données avant chaque test
        _current_db_session.query(Contact).delete()
        _current_db_session.commit()
        yield _current_db_session
    finally:
        _current_db_session.close()
        _current_db_session = None
        # Réinitialiser l'override
        app.dependency_overrides.clear()


def test_integration_odoo_to_db(db_session):
    """Test d'intégration : Récupération depuis Odoo et stockage en base de données."""
    # Vérifier que les variables d'environnement Odoo sont configurées
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    # 1. Récupérer les contacts depuis Odoo
    odoo_client = OdooClient()
    odoo_contacts = odoo_client.get_contacts()
    
    assert isinstance(odoo_contacts, list)
    assert len(odoo_contacts) > 0, "Aucun contact trouvé dans Odoo"
    
    # 2. Synchroniser les contacts dans la base de données
    for odoo_contact in odoo_contacts:
            contact_id = odoo_contact["id"]
            existing_contact = db_session.query(Contact).filter(Contact.id == contact_id).first()
            
            # Gérer le cas où Odoo retourne False pour un champ vide
            phone_value = odoo_contact.get("phone")
            if phone_value is False or phone_value == "":
                phone_value = None
            
            if existing_contact:
                # Mettre à jour
                existing_contact.name = odoo_contact.get("name")
                existing_contact.email = odoo_contact.get("email")
                existing_contact.phone = phone_value
            else:
                # Créer
                new_contact = Contact(
                    id=contact_id,
                    name=odoo_contact.get("name"),
                    email=odoo_contact.get("email"),
                    phone=phone_value,
                )
                db_session.add(new_contact)
    
    db_session.commit()
    
    # 3. Vérifier que les contacts sont bien en base de données
    db_contacts = db_session.query(Contact).all()
    assert len(db_contacts) == len(odoo_contacts), "Le nombre de contacts ne correspond pas"
    
    # 4. Vérifier que les données correspondent
    for odoo_contact in odoo_contacts:
        db_contact = db_session.query(Contact).filter(Contact.id == odoo_contact["id"]).first()
        assert db_contact is not None, f"Contact {odoo_contact['id']} non trouvé en base"
        assert db_contact.name == odoo_contact.get("name")
        assert db_contact.email == odoo_contact.get("email")
        # Gérer le cas où Odoo retourne False pour un champ vide
        odoo_phone = odoo_contact.get("phone")
        if odoo_phone is False or odoo_phone == "":
            odoo_phone = None
        assert db_contact.phone == odoo_phone or (db_contact.phone == "" and odoo_phone is None)


def test_integration_db_to_api(db_session):
    """Test d'intégration : Lecture depuis la base de données via l'API."""
    # Vérifier que les variables d'environnement sont configurées
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    # 1. Récupérer un contact depuis Odoo et l'insérer en base
    odoo_client = OdooClient()
    odoo_contacts = odoo_client.get_contacts()
    
    if not odoo_contacts:
        pytest.skip("Aucun contact dans Odoo pour tester")
    
    first_contact = odoo_contacts[0]
    contact_id = first_contact["id"]
    
    # Insérer en base
    phone_value = first_contact.get("phone")
    if phone_value is False or phone_value == "":
        phone_value = None
    
    db_contact = Contact(
        id=contact_id,
        name=first_contact.get("name"),
        email=first_contact.get("email"),
        phone=phone_value,
    )
    db_session.add(db_contact)
    db_session.commit()
    
    # 2. Obtenir un token JWT
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Calculer la signature HMAC
    import hashlib
    import hmac
    import time
    
    timestamp = str(int(time.time()))
    method = "GET"
    path = f"/contacts/{contact_id}"
    message = f"{method}{path}{timestamp}".encode()
    signature = hmac.new(
        settings.hmac_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    
    # 4. Récupérer le contact via l'API
    response = client.get(
        f"/contacts/{contact_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }
    )
    
    assert response.status_code == 200
    api_contact = response.json()
    
    # 5. Vérifier que les données correspondent
    assert api_contact["id"] == contact_id
    assert api_contact["name"] == first_contact.get("name")
    assert api_contact["email"] == first_contact.get("email")
    # Gérer le cas où Odoo retourne False pour un champ vide
    odoo_phone = first_contact.get("phone")
    if odoo_phone is False or odoo_phone == "":
        odoo_phone = None
    api_phone = api_contact.get("phone") or None
    assert api_phone == odoo_phone or (api_phone == "" and odoo_phone is None)


def test_integration_full_flow(db_session):
    """Test d'intégration complet : Odoo -> DB -> API."""
    # Vérifier que les variables d'environnement sont configurées
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    # 1. Récupérer les contacts depuis Odoo
    odoo_client = OdooClient()
    odoo_contacts = odoo_client.get_contacts()
    
    if not odoo_contacts:
        pytest.skip("Aucun contact dans Odoo pour tester")
    
    # 2. Synchroniser en base de données
    for odoo_contact in odoo_contacts:
            contact_id = odoo_contact["id"]
            existing_contact = db_session.query(Contact).filter(Contact.id == contact_id).first()
            
            if not existing_contact:
                # Gérer le cas où Odoo retourne False pour un champ vide
                phone_value = odoo_contact.get("phone")
                if phone_value is False or phone_value == "":
                    phone_value = None
                
                new_contact = Contact(
                    id=contact_id,
                    name=odoo_contact.get("name"),
                    email=odoo_contact.get("email"),
                    phone=phone_value,
                )
                db_session.add(new_contact)
    
    db_session.commit()
    
    # 3. Obtenir un token JWT
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 4. Récupérer tous les contacts via l'API
    import hashlib
    import hmac
    import time
    
    timestamp = str(int(time.time()))
    method = "GET"
    path = "/contacts"
    message = f"{method}{path}{timestamp}".encode()
    signature = hmac.new(
        settings.hmac_secret.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    
    response = client.get(
        "/contacts",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }
    )
    
    assert response.status_code == 200
    api_contacts = response.json()
    
    # 5. Vérifier que tous les contacts sont présents
    assert len(api_contacts) == len(odoo_contacts)
    
    # 6. Vérifier que les données correspondent
    api_contacts_dict = {c["id"]: c for c in api_contacts}
    for odoo_contact in odoo_contacts:
            contact_id = odoo_contact["id"]
            assert contact_id in api_contacts_dict, f"Contact {contact_id} manquant dans l'API"
            
            api_contact = api_contacts_dict[contact_id]
            assert api_contact["name"] == odoo_contact.get("name")
            assert api_contact["email"] == odoo_contact.get("email")
            # Gérer le cas où Odoo retourne False pour un champ vide
            odoo_phone = odoo_contact.get("phone")
            if odoo_phone is False or odoo_phone == "":
                odoo_phone = None
            api_phone = api_contact.get("phone") or None
            assert api_phone == odoo_phone or (api_phone == "" and odoo_phone is None)


def test_integration_fetch_endpoint():
    """Test d'intégration : Endpoint /fetch qui récupère directement depuis Odoo."""
    # Vérifier que les variables d'environnement sont configurées
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    # Appeler l'endpoint /fetch qui récupère directement depuis Odoo
    response = client.get("/fetch")
    
    assert response.status_code == 200
    contacts = response.json()
    
    assert isinstance(contacts, list)
    
    # Vérifier que les contacts ont la bonne structure
    if contacts:
        contact = contacts[0]
        assert "id" in contact
        assert "name" in contact
        assert "email" in contact
        assert "phone" in contact
