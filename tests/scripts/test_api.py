#!/usr/bin/env python3
"""Script pour tester l'API Odoo FastAPI avec calcul HMAC correct"""

import hashlib
import hmac
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

API_URL = "http://127.0.0.1:8000"
HMAC_SECRET = "HMACsecretTest222@@"


def calculate_hmac(method: str, path: str, timestamp: str, body: bytes = b"") -> str:
    """Calcule la signature HMAC selon la logique de security.py"""
    message = f"{method}{path}{timestamp}".encode() + body
    return hmac.new(
        HMAC_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()


def main():
    print("=== 1. Login pour obtenir un JWT ===\n")
    
    # Login
    login_data = urlencode({"username": "admin", "password": "admin"}).encode()
    req = Request(f"{API_URL}/auth/login", data=login_data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    with urlopen(req) as resp:
        token_data = json.loads(resp.read())
        print(json.dumps(token_data, indent=2))
        token = token_data["access_token"]
    
    print(f"\n✅ Token obtenu: {token[:50]}...\n")
    
    # GET /contacts
    print("=== 2. GET /contacts ===\n")
    timestamp = str(int(time.time()))
    method = "GET"
    path = "/contacts"
    signature = calculate_hmac(method, path, timestamp)
    
    req = Request(f"{API_URL}{path}")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Timestamp", timestamp)
    req.add_header("X-Signature", signature)
    
    try:
        with urlopen(req) as resp:
            contacts = json.loads(resp.read())
            print(json.dumps(contacts, indent=2))
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'read'):
            error_body = e.read().decode()
            print(f"Body de l'erreur: {error_body}")
    
    # GET /contacts/{id}
    print("\n=== 3. GET /contacts/1 ===\n")
    contact_id = 1
    timestamp = str(int(time.time()))
    method = "GET"
    path = f"/contacts/{contact_id}"
    signature = calculate_hmac(method, path, timestamp)
    
    req = Request(f"{API_URL}{path}")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("X-Timestamp", timestamp)
    req.add_header("X-Signature", signature)
    
    try:
        with urlopen(req) as resp:
            contact = json.loads(resp.read())
            print(json.dumps(contact, indent=2))
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'read'):
            error_body = e.read().decode()
            print(f"Body de l'erreur: {error_body}")


if __name__ == "__main__":
    main()
