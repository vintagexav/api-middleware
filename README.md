# Odoo Contacts API

FastAPI proxy vers Odoo (contacts) avec authentification JWT + HMAC.

## Description

Cette API middleware permet d'accéder aux contacts Odoo via une API REST sécurisée avec :
- **Authentification JWT** (JSON Web Tokens)
- **Vérification HMAC** pour l'intégrité des requêtes
- **Base de données** : SQLite en dev local, PostgreSQL en production (Vercel)
- **Endpoint direct** : `/fetch` récupère les contacts directement depuis Odoo
- **Endpoints sécurisés** : `/contacts` lit depuis la base de données

## Endpoints

**Base URL (Vercel)** : `https://api-middleware-two.vercel.app`

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/` | Non | Health check |
| `GET` | `/health` | Non | Health check détaillé (statut DB) |
| `GET` | `/fetch` | Non | Contacts récupérés en direct depuis Odoo |
| `POST` | `/auth/login` | Non | Obtenir un token JWT |
| `GET` | `/contacts` | JWT + HMAC | Contacts depuis la base de données |
| `GET` | `/contacts/{id}` | JWT + HMAC | Contact par ID depuis la base de données |

## Démarrage rapide (Local)

### Lancer le serveur

**Option 1: Script shell (recommandé pour développement local)**

```bash
# Depuis le répertoire du projet
./scripts/run_server.sh

# Ou avec options
./scripts/run_server.sh --kill          # Arrête automatiquement un serveur existant sur le port 8000
./scripts/run_server.sh --port 8001     # Utilise un port différent
```

**Option 2: Docker Compose (avec rechargement automatique)**

```bash
# Construire l'image une fois
docker-compose -f docker-compose.dev.yml build

# Lancer le serveur avec rechargement automatique
docker-compose -f docker-compose.dev.yml up

# Ou en arrière-plan
docker-compose -f docker-compose.dev.yml up -d

# Arrêter le serveur
docker-compose -f docker-compose.dev.yml down
```

Le serveur sera accessible sur :
- **API** : http://localhost:8000
- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc

### Exécuter les tests

```bash
# Depuis le répertoire du projet
./scripts/run_tests.sh

# Avec options pytest personnalisées
./scripts/run_tests.sh tests/test_contacts.py                    # Tester un fichier spécifique
./scripts/run_tests.sh tests/test_odoo_client.py                  # Tester le client Odoo
./scripts/run_tests.sh tests/integration/                         # Tester uniquement les tests d'intégration
./scripts/run_tests.sh tests/test_contacts.py::test_login_and_get_contacts  # Tester une fonction spécifique
./scripts/run_tests.sh --cov=app                                  # Avec couverture de code

# Script dédié pour les tests d'intégration
./scripts/run_integration_tests.sh                                # Exécuter uniquement les tests d'intégration
```

**Tests disponibles :**
- `tests/test_contacts.py` : Tests unitaires pour l'API FastAPI (6 tests)
- `tests/test_odoo_client.py` : Tests unitaires pour le client Odoo XML-RPC (5 tests)
- `tests/integration/test_integration.py` : Tests d'intégration complets (4 tests)
  - Teste le flux complet : Odoo → Base de données → API
  - Nécessite une connexion active à Odoo

Voir [tests/README.md](tests/README.md) pour plus de détails sur les tests.

## Prérequis

- Python >= 3.12
- `uv` (gestionnaire de paquets Python)
- Accès à une instance Odoo

## Installation

```bash
# Installer les dépendances avec uv
uv sync
```

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration Odoo
ODOO_URL=http://your-odoo-instance.com
ODOO_DB=your_database
ODOO_USER=your_username
ODOO_PASSWORD=your_password

# Sécurité
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRE_MINUTES=60
HMAC_SECRET=your-hmac-secret-key

# Authentification de démo
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Base de données
# SQLite pour le développement local (par défaut)
DATABASE_URL=sqlite:///./contacts.db
# PostgreSQL pour la production (Vercel, Render, etc.)
# DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Synchronisation des contacts (dev local)

En développement local avec SQLite, vous pouvez synchroniser les contacts depuis Odoo vers la base de données.

> **Note** : Cette synchronisation par cron est prévue pour un serveur persistant. Sur Vercel (serverless), utilisez l'endpoint `/fetch` ou une base PostgreSQL alimentée autrement.

### Synchronisation manuelle

```bash
# Synchroniser une fois les contacts depuis Odoo
uv run python sync_contacts.py
```

### Synchronisation automatique (Cron)

Pour synchroniser automatiquement les contacts toutes les 5 minutes :

#### Option 1 : Script d'installation automatique

```bash
./scripts/install_cron.sh
```

#### Option 2 : Installation manuelle

1. Éditez le fichier `crontab.example` et ajustez les chemins
2. Installez-le avec : `crontab crontab.example`
3. Vérifiez avec : `crontab -l`

**Note** : La synchronisation crée automatiquement la base de données et les tables si elles n'existent pas.

## Endpoints API

### POST `/auth/login`
Authentification pour obtenir un token JWT.

**Body (form-data)** :
- `username` : Nom d'utilisateur
- `password` : Mot de passe

**Réponse** :
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET `/contacts`
Récupère tous les contacts depuis la base de données.

**Headers requis** :
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Réponse** :
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123456789"
  }
]
```

### GET `/contacts/{contact_id}`
Récupère un contact spécifique par ID.

**Headers requis** :
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Réponse** :
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "123456789"
}
```

## Sécurité

### JWT (JSON Web Tokens)
- Utilisé pour authentifier les utilisateurs
- Obtenu via `/auth/login`
- Inclus dans le header `Authorization: Bearer <token>`

### HMAC Signature
Chaque requête protégée (`/contacts`) doit inclure :
- `X-Timestamp` : Timestamp Unix de la requête
- `X-Signature` : Signature HMAC-SHA256 calculée comme suit :

```
message = method + path + timestamp + body
signature = HMAC-SHA256(hmac_secret, message)
```

La signature doit être calculée avec le secret `HMAC_SECRET` configuré.

## Structure du projet

```
api-middleware/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application FastAPI principale
│   ├── config.py        # Configuration (pydantic-settings)
│   ├── database.py      # Configuration SQLAlchemy
│   ├── models.py        # Modèles de base de données (Contact)
│   ├── db_client.py     # Client pour lire depuis la DB
│   ├── odoo_client.py   # Client XML-RPC pour Odoo
│   └── security.py      # Authentification JWT + HMAC
├── api/
│   ├── __init__.py
│   └── index.py         # Handler Vercel
├── scripts/
│   ├── install_cron.sh          # Script d'installation du cron
│   ├── run_server.sh            # Script pour lancer le serveur localement
│   ├── run_tests.sh             # Script pour exécuter tous les tests
│   ├── run_integration_tests.sh # Script pour exécuter uniquement les tests d'intégration
│   └── sync_with_env.sh         # Sync avec chargement du .env
├── tests/
│   ├── __init__.py
│   ├── README.md        # Documentation des tests
│   ├── test_contacts.py      # Tests unitaires API FastAPI
│   ├── test_odoo_client.py   # Tests unitaires client Odoo
│   ├── scripts/              # Scripts de test manuels
│   │   ├── README.md         # Documentation des scripts de test
│   │   ├── test_api_improved.py  # Test API locale (avec gestion d'erreurs)
│   │   ├── test_vercel.py         # Test API Vercel (complet)
│   │   ├── test_vercel_debug.py   # Test API Vercel (debug HMAC)
│   │   ├── test_odoo_complete.py  # Test complet Odoo (direct + FastAPI)
│   │   ├── test_import.py          # Test d'imports
│   │   ├── test_api.sh             # Script shell pour tester l'API locale
│   │   └── test_vercel.sh          # Script shell pour tester l'API Vercel
│   └── integration/                # Tests d'intégration
│       ├── __init__.py
│       └── test_integration.py     # Tests d'intégration complets (Odoo -> DB -> API)
├── sync_contacts.py     # Script de synchronisation Odoo -> DB
├── init_db.py           # Initialisation de la base de données
├── crontab.example      # Exemple de configuration cron
├── pyproject.toml       # Configuration du projet et dépendances
├── requirements.txt     # Dépendances (utilisé par Vercel)
├── uv.lock              # Lock file pour uv (gestionnaire de paquets)
├── vercel.json          # Configuration Vercel
├── Dockerfile           # Image Docker
├── render.yaml          # Configuration Render.com
├── VERCEL_DEPLOY.md     # Guide de déploiement Vercel
└── README.md            # Ce fichier
```

## Développement

### Installer les dépendances de développement

```bash
uv sync --dev
```

### Tests

Les tests sont organisés dans le dossier `tests/` :

```
tests/
├── __init__.py              # Package Python
├── README.md                # Documentation des tests
├── test_contacts.py         # Tests unitaires API FastAPI
├── test_odoo_client.py      # Tests unitaires client Odoo
├── integration/             # Tests d'intégration
│   ├── __init__.py
│   └── test_integration.py  # Tests d'intégration complets (Odoo -> DB -> API)
└── scripts/                 # Scripts de test manuels
    ├── README.md            # Documentation des scripts de test
    ├── test_api_improved.py # Test API locale
    ├── test_vercel.py       # Test API Vercel
    ├── test_odoo_complete.py # Test Odoo complet
    └── ...                  # Autres scripts de test
```

**Exécution des tests** : Utilisez `./scripts/run_tests.sh` (voir section "Démarrage rapide" ci-dessus).

**Tests unitaires (`test_contacts.py`)** :
- Authentification et récupération des contacts
- Récupération d'un contact par ID
- Gestion des contacts non trouvés
- Rejet des identifiants invalides
- Rejet des requêtes sans JWT
- Rejet des requêtes sans signature HMAC

**Tests unitaires (`test_odoo_client.py`)** :
- Initialisation du client Odoo
- Récupération de tous les contacts depuis Odoo
- Récupération d'un contact par ID
- Gestion d'un ID inexistant
- Validation des variables d'environnement

**Tests d'intégration (`test_integration.py`)** :
- `test_integration_odoo_to_db` : Récupération depuis Odoo et stockage en base de données
- `test_integration_db_to_api` : Lecture depuis la base de données via l'API
- `test_integration_full_flow` : Flux complet Odoo → DB → API
- `test_integration_fetch_endpoint` : Endpoint `/fetch` qui récupère directement depuis Odoo

**Note** : Les tests d'intégration nécessitent une connexion active à Odoo et testent le flux complet du système de bout en bout.

Les tests utilisent une base SQLite temporaire et surchargent la dépendance `get_db` de FastAPI pour isoler les tests de la base de production.

**Scripts de test manuels** : Les scripts dans `tests/scripts/` permettent de tester l'API manuellement (locale ou Vercel). Voir [tests/README.md](tests/README.md) pour plus de détails.

## Architecture

### Deux modes d'accès aux contacts

1. **Direct** (`/fetch`) : Appel XML-RPC à Odoo en temps réel
2. **Via base de données** (`/contacts`) : Lecture depuis SQLite/PostgreSQL, alimentée par `sync_contacts.py`

### Flux de synchronisation (dev local)

1. `sync_contacts.py` se connecte à Odoo via XML-RPC
2. Récupère tous les contacts
3. Synchronise la base de données :
   - **Insère** les nouveaux contacts
   - **Met à jour** les contacts existants
   - **Supprime** les contacts qui n'existent plus dans Odoo
4. L'API lit les contacts depuis la base de données

## Déploiement

### Vercel (production)

Pour déployer sur Vercel, consultez le guide détaillé : [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)

```bash
npm i -g vercel
vercel --prod
```

Configurez `DATABASE_URL` avec une base PostgreSQL dans les variables d'environnement Vercel (SQLite ne fonctionne pas en serverless).

### Docker

#### Production

```bash
docker build -t odoo-contacts-api .
docker run -p 8000:8000 --env-file .env odoo-contacts-api
```

#### Development (with live reload - no rebuild needed)

**Option 1: Using docker-compose (recommended)**

```bash
# Build once
docker-compose -f docker-compose.dev.yml build

# Run with live reloading
docker-compose -f docker-compose.dev.yml up

# Or run in detached mode
docker-compose -f docker-compose.dev.yml up -d
```

**Option 2: Using docker run directly**

```bash
# Build once
docker build -t odoo-contacts-api .

# Run with volume mount for live reloading
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd):/app \
  -v /app/.venv \
  odoo-contacts-api \
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

With these commands, changes to your code files will automatically reload the server without needing to rebuild the Docker image.

### Render.com

Le fichier `render.yaml` est fourni pour un déploiement sur Render. Les secrets JWT et HMAC sont générés automatiquement.
