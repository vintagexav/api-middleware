import hashlib
import hmac
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Contact

# Créer une base de données temporaire pour les tests (fichier temporaire)
import tempfile
import os

# Créer un fichier temporaire pour la base de données
temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
temp_db.close()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db.name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables une seule fois au niveau du module
Base.metadata.create_all(bind=engine)

# Nettoyer le fichier temporaire après les tests
import atexit
atexit.register(lambda: os.unlink(temp_db.name) if os.path.exists(temp_db.name) else None)


def override_get_db():
    """Override de get_db pour utiliser une base de données de test."""
    # S'assurer que les tables existent
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Remplacer la dépendance get_db
app.dependency_overrides[get_db] = override_get_db

# Créer le client de test
client = TestClient(app)

HMAC_SECRET = "HMACsecretTest222@@"


def setup_test_db():
    """Initialise la base de données de test avec des données."""
    db = TestingSessionLocal()
    try:
        # Nettoyer les données existantes
        db.query(Contact).delete()
        
        # Créer un contact de test
        test_contact = Contact(
            id=1,
            name="John Doe",
            email="john@example.com",
            phone="123",
        )
        db.add(test_contact)
        db.commit()
    finally:
        db.close()


def calculate_hmac(method: str, path: str, timestamp: str, body: bytes = b"") -> str:
    """Calcule la signature HMAC pour les tests"""
    message = f"{method}{path}{timestamp}".encode() + body
    return hmac.new(
        HMAC_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def test_login_and_get_contacts():
    setup_test_db()  # Réinitialiser les données avant chaque test
    
    # login
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # Calculer HMAC pour /contacts
    timestamp = str(int(time.time()))
    signature = calculate_hmac("GET", "/contacts", timestamp)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }
    resp2 = client.get("/contacts", headers=headers)
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), list)
    assert len(resp2.json()) > 0


def test_get_contact_by_id():
    setup_test_db()  # Réinitialiser les données avant chaque test
    
    # login
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # Calculer HMAC pour /contacts/1
    timestamp = str(int(time.time()))
    signature = calculate_hmac("GET", "/contacts/1", timestamp)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }
    resp2 = client.get("/contacts/1", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == 1


def test_get_contact_not_found():
    setup_test_db()  # Réinitialiser les données avant chaque test
    
    # login
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    # Calculer HMAC pour /contacts/999
    timestamp = str(int(time.time()))
    signature = calculate_hmac("GET", "/contacts/999", timestamp)

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }
    resp2 = client.get("/contacts/999", headers=headers)
    assert resp2.status_code == 404
    assert "not found" in resp2.json()["detail"].lower()


def test_login_invalid_credentials():
    resp = client.post(
        "/auth/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert resp.status_code == 400


def test_contacts_without_jwt():
    timestamp = str(int(time.time()))
    signature = calculate_hmac("GET", "/contacts", timestamp)
    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }
    resp = client.get("/contacts", headers=headers)
    assert resp.status_code == 401


def test_contacts_without_hmac():
    resp = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/contacts", headers=headers)
    assert resp2.status_code == 403
