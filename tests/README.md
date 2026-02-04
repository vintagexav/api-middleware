# Tests

Ce dossier contient tous les tests du projet.

## Structure

```
tests/
├── test_contacts.py          # Tests unitaires pour l'API contacts
├── test_odoo_client.py       # Tests unitaires pour le client Odoo (XML-RPC)
├── scripts/                  # Scripts de test manuels
│   ├── test_api.py          # Test API locale (basique)
│   ├── test_api_improved.py # Test API locale (amélioré)
│   ├── test_vercel.py       # Test API Vercel
│   ├── test_vercel_debug.py # Test API Vercel (debug)
│   ├── test_import.py       # Test d'imports
│   ├── test_api.sh          # Script shell pour tester l'API locale
│   └── test_vercel.sh       # Script shell pour tester l'API Vercel
└── integration/             # Tests d'intégration (vide pour l'instant)
```

## Exécution des tests

### Tests unitaires (automatisés)

Pour exécuter tous les tests unitaires :

```bash
./scripts/run_tests.sh
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

### Scripts de test manuels

Les scripts dans `tests/scripts/` sont des outils de test manuels pour tester l'API de différentes manières. Voir [tests/scripts/README.md](scripts/README.md) pour plus de détails.

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

## Configuration

Les tests nécessitent les variables d'environnement suivantes :

- `ODOO_URL` : URL de l'instance Odoo
- `ODOO_DB` : Nom de la base de données Odoo
- `ODOO_USER` : Nom d'utilisateur Odoo
- `ODOO_PASSWORD` : Mot de passe Odoo
- `HMAC_SECRET` : Secret pour HMAC (par défaut: `HMACsecretTest222@@`)
- `JWT_SECRET` : Secret pour JWT (par défaut: `JWTSEcret11@@`)

Ces variables peuvent être définies dans un fichier `.env` à la racine du projet.
