# Tests

Ce dossier contient tous les tests du projet.

## Structure

```
tests/
├── __init__.py              # Package Python
├── README.md                # Documentation des tests (ce fichier)
├── test_contacts.py         # Tests unitaires pour l'API contacts
├── test_odoo_client.py      # Tests unitaires pour le client Odoo (XML-RPC)
├── scripts/                 # Scripts de test manuels
│   ├── README.md            # Documentation des scripts de test
│   ├── test_api_improved.py # Test API locale (avec gestion d'erreurs)
│   ├── test_vercel.py       # Test API Vercel (complet)
│   ├── test_vercel_debug.py # Test API Vercel (debug HMAC)
│   ├── test_odoo_complete.py # Test complet Odoo (direct + FastAPI)
│   ├── test_import.py       # Test d'imports
│   ├── test_api.sh          # Script shell pour tester l'API locale
│   └── test_vercel.sh       # Script shell pour tester l'API Vercel
└── integration/              # Tests d'intégration
    ├── __init__.py
    └── test_integration.py  # Tests d'intégration complets (Odoo -> DB -> API)
```

## Exécution des tests

### Tests unitaires (automatisés)

Pour exécuter tous les tests (unitaires + intégration) :

```bash
./scripts/run_tests.sh
```

**Note** : Par défaut, `run_tests.sh` exécute tous les tests, y compris les tests d'intégration. Pour exécuter uniquement les tests unitaires, utilisez :

```bash
./scripts/run_tests.sh tests/test_contacts.py tests/test_odoo_client.py
```

Pour exécuter un fichier de test spécifique :

```bash
./scripts/run_tests.sh tests/test_contacts.py
./scripts/run_tests.sh tests/test_odoo_client.py
```

Pour exécuter un test spécifique :

```bash
./scripts/run_tests.sh tests/test_contacts.py::test_login_and_get_contacts
```

Pour exécuter les tests d'intégration :

```bash
# Utiliser le script dédié (recommandé)
./scripts/run_integration_tests.sh

# Ou via run_tests.sh
./scripts/run_tests.sh tests/integration/
```

### Scripts de test manuels

Les scripts dans `tests/scripts/` sont des outils de test manuels pour tester l'API de différentes manières :

- **Tests API FastAPI locale** : `test_api_improved.py` (avec gestion d'erreurs améliorée)
- **Tests API Vercel** : `test_vercel.py` (complet), `test_vercel_debug.py` (debug HMAC)
- **Tests Odoo** : `test_odoo_complete.py` (direct XML-RPC + FastAPI)
- **Utilitaires** : `test_import.py` (vérification des imports)
- **Scripts shell** : `test_api.sh`, `test_vercel.sh` (tests avec curl)

Voir [tests/scripts/README.md](scripts/README.md) pour plus de détails et exemples d'utilisation.

## Tests unitaires

### `test_contacts.py`
Tests pour l'API FastAPI (endpoints `/contacts`, authentification JWT + HMAC).

**Tests inclus :**
- Authentification et récupération des contacts
- Récupération d'un contact par ID
- Gestion des contacts non trouvés
- Rejet des identifiants invalides
- Rejet des requêtes sans JWT
- Rejet des requêtes sans signature HMAC

### `test_odoo_client.py`
Tests pour le client Odoo utilisant XML-RPC.

**Tests inclus :**
- Initialisation du client Odoo
- Récupération de tous les contacts
- Récupération d'un contact par ID
- Gestion d'un ID inexistant
- Validation des variables d'environnement

### `test_integration.py`
Tests d'intégration pour vérifier le flux complet du système.

**Tests inclus :**
- `test_integration_odoo_to_db` : Récupération depuis Odoo et stockage en base de données
- `test_integration_db_to_api` : Lecture depuis la base de données via l'API
- `test_integration_full_flow` : Flux complet Odoo -> DB -> API
- `test_integration_fetch_endpoint` : Endpoint `/fetch` qui récupère directement depuis Odoo

**Note :** Ces tests nécessitent une connexion active à Odoo et testent l'intégration complète du système.

## Configuration

Les tests nécessitent les variables d'environnement suivantes :

- `ODOO_URL` : URL de l'instance Odoo
- `ODOO_DB` : Nom de la base de données Odoo
- `ODOO_USER` : Nom d'utilisateur Odoo
- `ODOO_PASSWORD` : Mot de passe Odoo
- `HMAC_SECRET` : Secret pour HMAC (par défaut: `HMACsecretTest222@@`)
- `JWT_SECRET` : Secret pour JWT (par défaut: `JWTSEcret11@@`)

Ces variables peuvent être définies dans un fichier `.env` à la racine du projet.
