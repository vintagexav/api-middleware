# Scripts de test manuels

Ce dossier contient des scripts de test manuels pour tester l'API de différentes manières.

## Scripts Python

### Tests API FastAPI (locale)

#### `test_api_improved.py`
Script pour tester l'API locale avec calcul HMAC correct et gestion d'erreurs améliorée.

**Usage:**
```bash
uv run python tests/scripts/test_api_improved.py
# ou
python3 tests/scripts/test_api_improved.py
```

**Teste :**
- Authentification (login)
- GET `/contacts` avec JWT + HMAC
- GET `/contacts/{id}` avec JWT + HMAC

### Tests API FastAPI (Vercel)

#### `test_vercel.py`
Script complet pour tester l'API déployée sur Vercel avec tous les endpoints.

**Usage:**
```bash
uv run python tests/scripts/test_vercel.py
# ou
python3 tests/scripts/test_vercel.py
```

**Teste :**
- Accessibilité de l'API
- Authentification (login)
- GET `/contacts` avec JWT + HMAC
- GET `/contacts/{id}` avec JWT + HMAC
- Tests de sécurité (sans JWT, sans HMAC)
- Documentation API

#### `test_vercel_debug.py`
Version de debug avec affichage détaillé pour diagnostiquer les problèmes HMAC sur Vercel.

**Usage:**
```bash
uv run python tests/scripts/test_vercel_debug.py
# ou
python3 tests/scripts/test_vercel_debug.py
```

**Utile pour :**
- Déboguer les problèmes de signature HMAC
- Voir les détails des calculs HMAC
- Vérifier les headers envoyés

### Tests Odoo (XML-RPC)

#### `test_odoo_complete.py`
Script complet pour tester les appels API à Odoo (direct via XML-RPC et via FastAPI).

**Usage:**
```bash
uv run python tests/scripts/test_odoo_complete.py
# ou
python3 tests/scripts/test_odoo_complete.py
```

**Teste :**
- Connexion directe à Odoo via XML-RPC
- Récupération de tous les contacts depuis Odoo
- Récupération d'un contact par ID
- Endpoint FastAPI `/fetch` (si le serveur est démarré)

**Note :** Nécessite les variables d'environnement Odoo configurées (`ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`).

### Utilitaires

#### `test_import.py`
Test d'import pour vérifier que tous les modules peuvent être importés correctement (utile pour Vercel).

**Usage:**
```bash
uv run python tests/scripts/test_import.py
# ou
python3 tests/scripts/test_import.py
```

## Scripts Shell

### `test_api.sh`
Script bash pour tester l'API locale avec curl.

**Usage:**
```bash
./tests/scripts/test_api.sh
```

**Teste :**
- Authentification (login)
- GET `/contacts` avec JWT + HMAC
- GET `/contacts/{id}` avec JWT + HMAC

### `test_vercel.sh`
Script bash complet pour tester l'API Vercel avec curl.

**Usage:**
```bash
./tests/scripts/test_vercel.sh
```

**Teste :**
- Accessibilité de l'API
- Authentification (login)
- GET `/contacts` avec JWT + HMAC
- GET `/contacts/{id}` avec JWT + HMAC
- Tests de sécurité
- Documentation API

## Note

Ces scripts sont des outils de test manuels et ne font pas partie de la suite de tests automatisés. Pour exécuter les tests unitaires, utilisez :

```bash
./scripts/run_tests.sh
```

## Recommandations

- **Pour tester l'API locale** : Utilisez `test_api_improved.py` ou `test_api.sh`
- **Pour tester l'API Vercel** : Utilisez `test_vercel.py` ou `test_vercel.sh`
- **Pour déboguer les problèmes HMAC** : Utilisez `test_vercel_debug.py`
- **Pour tester Odoo** : Utilisez `test_odoo_complete.py`
