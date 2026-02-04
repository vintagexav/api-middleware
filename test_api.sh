#!/bin/bash

# Script pour tester l'API Odoo FastAPI
# Usage: ./test_api.sh

API_URL="http://127.0.0.1:8000"
HMAC_SECRET="HMACsecretTest222@@"
JWT_SECRET="JWTSEcret11@@"

echo "=== 1. Login pour obtenir un JWT ==="
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin")

echo "$TOKEN_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo "❌ Échec du login"
  exit 1
fi

echo ""
echo "Token JWT obtenu: ${TOKEN:0:50}..."
echo ""

# Fonction pour calculer HMAC
calculate_hmac() {
  local method=$1
  local path=$2
  local timestamp=$3
  local body=$4
  local message="${method}${path}${timestamp}${body}"
  echo -n "$message" | openssl dgst -sha256 -hmac "$HMAC_SECRET" | cut -d' ' -f2
}

echo "=== 2. GET /contacts (avec JWT + HMAC) ==="
TIMESTAMP=$(date +%s)
METHOD="GET"
PATH="/contacts"
BODY=""
SIGNATURE=$(calculate_hmac "$METHOD" "$PATH" "$TIMESTAMP" "$BODY")

curl -v -X GET "$API_URL/contacts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE" \
  | python3 -m json.tool

echo ""
echo "=== 3. GET /contacts/{id} (exemple avec ID=1) ==="
CONTACT_ID=1
TIMESTAMP=$(date +%s)
METHOD="GET"
PATH="/contacts/$CONTACT_ID"
BODY=""
SIGNATURE=$(calculate_hmac "$METHOD" "$PATH" "$TIMESTAMP" "$BODY")

curl -v -X GET "$API_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE" \
  | python3 -m json.tool
