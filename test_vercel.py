#!/usr/bin/env python3
"""Script pour tester l'API déployée sur Vercel."""
import hashlib
import hmac
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

API_URL = "https://api-middleware-two.vercel.app"
HMAC_SECRET = "HMACsecretTest222@@"


def calculate_hmac(method: str, path: str, timestamp: str, body: bytes = b"") -> str:
    """Calcule la signature HMAC."""
    message = f"{method}{path}{timestamp}".encode() + body
    return hmac.new(
        HMAC_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def test_api():
    """Teste l'API Vercel."""
    print("🧪 Test de l'API Vercel:", API_URL)
    print()

    # Test 1: Vérifier l'accessibilité
    print("=== 1. Vérification de l'accessibilité de l'API ===")
    try:
        req = Request(f"{API_URL}/docs")
        with urlopen(req) as resp:
            if resp.getcode() == 200:
                print("✅ API accessible (HTTP 200)")
            else:
                print(f"⚠️  Code HTTP: {resp.getcode()}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    print()

    # Test 2: Login
    print("=== 2. Authentification (Login) ===")
    try:
        login_data = urlencode({"username": "admin", "password": "admin"}).encode()
        req = Request(f"{API_URL}/auth/login", data=login_data, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urlopen(req) as resp:
            token_data = json.loads(resp.read())
            print(json.dumps(token_data, indent=2))
            token = token_data["access_token"]
            print(f"\n✅ Token JWT obtenu: {token[:50]}...")
    except Exception as e:
        print(f"❌ Échec du login: {e}")
        return False
    print()

    # Test 3: GET /contacts
    print("=== 3. GET /contacts (avec JWT + HMAC) ===")
    try:
        timestamp = str(int(time.time()))
        signature = calculate_hmac("GET", "/contacts", timestamp)

        req = Request(f"{API_URL}/contacts")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-Timestamp", timestamp)
        req.add_header("X-Signature", signature)

        with urlopen(req) as resp:
            contacts = json.loads(resp.read())
            print(f"✅ Requête réussie (HTTP {resp.getcode()})")
            print(json.dumps(contacts, indent=2))
    except HTTPError as e:
        print(f"❌ Requête échouée (HTTP {e.code})")
        error_body = e.read().decode()
        print(f"Réponse: {error_body}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()

    # Test 4: GET /contacts/1
    print("=== 4. GET /contacts/1 (avec JWT + HMAC) ===")
    try:
        contact_id = 1
        timestamp = str(int(time.time()))
        signature = calculate_hmac("GET", f"/contacts/{contact_id}", timestamp)

        req = Request(f"{API_URL}/contacts/{contact_id}")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("X-Timestamp", timestamp)
        req.add_header("X-Signature", signature)

        with urlopen(req) as resp:
            contact = json.loads(resp.read())
            print(f"✅ Requête réussie (HTTP {resp.getcode()})")
            print(json.dumps(contact, indent=2))
    except HTTPError as e:
        if e.code == 404:
            print(f"⚠️  Contact non trouvé (HTTP {e.code}) - Normal si la DB est vide")
        else:
            print(f"❌ Requête échouée (HTTP {e.code})")
        error_body = e.read().decode()
        print(f"Réponse: {error_body}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()

    # Test 5: Test sans JWT
    print("=== 5. Test sans JWT (devrait échouer avec 401) ===")
    try:
        timestamp = str(int(time.time()))
        signature = calculate_hmac("GET", "/contacts", timestamp)

        req = Request(f"{API_URL}/contacts")
        req.add_header("X-Timestamp", timestamp)
        req.add_header("X-Signature", signature)

        with urlopen(req) as resp:
            print(f"⚠️  Code HTTP inattendu: {resp.getcode()} (attendu: 401)")
    except HTTPError as e:
        if e.code == 401:
            print(f"✅ Sécurité fonctionne: Requête rejetée sans JWT (HTTP {e.code})")
        else:
            print(f"⚠️  Code HTTP: {e.code} (attendu: 401)")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()

    # Test 6: Test sans HMAC
    print("=== 6. Test sans HMAC (devrait échouer avec 403) ===")
    try:
        req = Request(f"{API_URL}/contacts")
        req.add_header("Authorization", f"Bearer {token}")

        with urlopen(req) as resp:
            print(f"⚠️  Code HTTP inattendu: {resp.getcode()} (attendu: 403)")
    except HTTPError as e:
        if e.code == 403:
            print(f"✅ Sécurité fonctionne: Requête rejetée sans HMAC (HTTP {e.code})")
        else:
            print(f"⚠️  Code HTTP: {e.code} (attendu: 403)")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()

    # Test 7: Documentation
    print("=== 7. Documentation API ===")
    try:
        req = Request(f"{API_URL}/docs")
        with urlopen(req) as resp:
            if resp.getcode() == 200:
                print(f"✅ Documentation accessible: {API_URL}/docs")
            else:
                print(f"⚠️  Code HTTP: {resp.getcode()}")
    except Exception as e:
        print(f"⚠️  Documentation non accessible: {e}")
    print()

    print("🎉 Tests terminés!")
    print()
    print("📝 Liens utiles:")
    print(f"   - API: {API_URL}")
    print(f"   - Documentation: {API_URL}/docs")
    print(f"   - ReDoc: {API_URL}/redoc")

    return True


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
