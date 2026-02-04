#!/bin/bash

# Script pour tester l'API déployée sur Vercel
# Usage: ./test_vercel.sh

API_URL="https://api-middleware-two.vercel.app"
HMAC_SECRET="HMACsecretTest222@@"
JWT_SECRET="JWTSEcret11@@"

echo "🧪 Test de l'API Vercel: $API_URL"
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

# Test 1: Vérifier que l'API est accessible
echo "=== 1. Vérification de l'accessibilité de l'API ==="
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$HTTP_STATUS" == "200" ]; then
  echo "✅ API accessible (HTTP $HTTP_STATUS)"
else
  echo "❌ API non accessible (HTTP $HTTP_STATUS)"
  exit 1
fi
echo ""

# Test 2: Login pour obtenir un JWT
echo "=== 2. Authentification (Login) ==="
TOKEN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin")

echo "$TOKEN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TOKEN_RESPONSE"

TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Échec du login"
  exit 1
fi

echo ""
echo "✅ Token JWT obtenu: ${TOKEN:0:50}..."
echo ""

# Test 3: GET /contacts (avec JWT + HMAC)
echo "=== 3. GET /contacts (avec JWT + HMAC) ==="
TIMESTAMP=$(date +%s)
METHOD="GET"
PATH="/contacts"
BODY=""
SIGNATURE=$(calculate_hmac "$METHOD" "$PATH" "$TIMESTAMP" "$BODY")

RESPONSE=$(curl -s -X GET "$API_URL/contacts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE")

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/contacts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE")

if [ "$HTTP_CODE" == "200" ]; then
  echo "✅ Requête réussie (HTTP $HTTP_CODE)"
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
  echo "❌ Requête échouée (HTTP $HTTP_CODE)"
  echo "Réponse: $RESPONSE"
fi
echo ""

# Test 4: GET /contacts/{id} (exemple avec ID=1)
echo "=== 4. GET /contacts/1 (avec JWT + HMAC) ==="
CONTACT_ID=1
TIMESTAMP=$(date +%s)
METHOD="GET"
PATH="/contacts/$CONTACT_ID"
BODY=""
SIGNATURE=$(calculate_hmac "$METHOD" "$PATH" "$TIMESTAMP" "$BODY")

RESPONSE=$(curl -s -X GET "$API_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE")

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/contacts/$CONTACT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE")

if [ "$HTTP_CODE" == "200" ]; then
  echo "✅ Requête réussie (HTTP $HTTP_CODE)"
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
elif [ "$HTTP_CODE" == "404" ]; then
  echo "⚠️  Contact non trouvé (HTTP $HTTP_CODE) - Normal si la DB est vide"
  echo "$RESPONSE"
else
  echo "❌ Requête échouée (HTTP $HTTP_CODE)"
  echo "Réponse: $RESPONSE"
fi
echo ""

# Test 5: Test sans JWT (devrait échouer avec 401)
echo "=== 5. Test sans JWT (devrait échouer) ==="
TIMESTAMP=$(date +%s)
SIGNATURE=$(calculate_hmac "GET" "/contacts" "$TIMESTAMP" "")
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/contacts" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Signature: $SIGNATURE")

if [ "$HTTP_CODE" == "401" ]; then
  echo "✅ Sécurité fonctionne: Requête rejetée sans JWT (HTTP $HTTP_CODE)"
else
  echo "⚠️  Code HTTP inattendu: $HTTP_CODE (attendu: 401)"
fi
echo ""

# Test 6: Test sans HMAC (devrait échouer avec 403)
echo "=== 6. Test sans HMAC (devrait échouer) ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/contacts" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" == "403" ]; then
  echo "✅ Sécurité fonctionne: Requête rejetée sans HMAC (HTTP $HTTP_CODE)"
else
  echo "⚠️  Code HTTP inattendu: $HTTP_CODE (attendu: 403)"
fi
echo ""

# Test 7: Documentation API
echo "=== 7. Documentation API ==="
DOC_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$DOC_STATUS" == "200" ]; then
  echo "✅ Documentation accessible: $API_URL/docs"
else
  echo "⚠️  Documentation non accessible (HTTP $DOC_STATUS)"
fi
echo ""

echo "🎉 Tests terminés!"
echo ""
echo "📝 Liens utiles:"
echo "   - API: $API_URL"
echo "   - Documentation: $API_URL/docs"
echo "   - ReDoc: $API_URL/redoc"
