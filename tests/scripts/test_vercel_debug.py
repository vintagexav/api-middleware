#!/usr/bin/env python3
"""Script de debug pour tester l'API Vercel avec affichage détaillé."""
import hashlib
import hmac
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_URL = "https://api-middleware-two.vercel.app"
HMAC_SECRET = "HMACsecretTest222@@"


def calculate_hmac(method: str, path: str, timestamp: str, body: bytes = b"") -> str:
    """Calcule la signature HMAC avec debug."""
    message = f"{method}{path}{timestamp}".encode() + body
    signature = hmac.new(
        HMAC_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()
    
    print(f"  Debug HMAC:")
    print(f"    Method: {method}")
    print(f"    Path: {path}")
    print(f"    Timestamp: {timestamp}")
    print(f"    Message (bytes): {message}")
    print(f"    HMAC Secret: {HMAC_SECRET}")
    print(f"    Signature: {signature}")
    
    return signature


# Test de login
print("=== Login ===")
login_data = f"username=admin&password=admin".encode()
req = Request(f"{API_URL}/auth/login", data=login_data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")

with urlopen(req) as resp:
    token_data = json.loads(resp.read())
    token = token_data["access_token"]
    print(f"Token obtenu: {token[:50]}...")
print()

# Test GET /contacts avec debug
print("=== GET /contacts avec debug ===")
timestamp = str(int(time.time()))
path = "/contacts"
signature = calculate_hmac("GET", path, timestamp)

req = Request(f"{API_URL}{path}")
req.add_header("Authorization", f"Bearer {token}")
req.add_header("X-Timestamp", timestamp)
req.add_header("X-Signature", signature)

print(f"\n  Headers envoyés:")
print(f"    Authorization: Bearer {token[:20]}...")
print(f"    X-Timestamp: {timestamp}")
print(f"    X-Signature: {signature}")

try:
    with urlopen(req) as resp:
        contacts = json.loads(resp.read())
        print(f"\n✅ Succès!")
        print(json.dumps(contacts, indent=2))
except HTTPError as e:
    print(f"\n❌ Erreur HTTP {e.code}")
    error_body = e.read().decode()
    print(f"Réponse: {error_body}")
