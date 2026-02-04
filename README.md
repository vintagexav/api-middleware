# Odoo Contacts API

## Endpoints

Base URL (Vercel) : `https://api-middleware-two.vercel.app`

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/` | Non | Health check |
| `GET` | `/health` | Non | Health check détaillé (statut DB) |
| `GET` | `/fetch` | Non | Contacts récupérés en direct depuis Odoo |
| `POST` | `/auth/login` | Non | Obtenir un token JWT |
| `GET` | `/contacts` | JWT + HMAC | Contacts depuis la base de données |
| `GET` | `/contacts/{id}` | JWT + HMAC | Contact par ID depuis la base de données |

FastAPI proxy vers Odoo (contacts) avec authentification JWT + HMAC.

## Description

Cette API middleware permet d'accéder aux contacts Odoo via une API REST sécurisée avec :
- **Authentification JWT** (JSON Web Tokens)
- **Vérification HMAC** pour l'intégrité des requêtes
- **Base de données** : SQLite en dev local, PostgreSQL en production (Vercel)
- **Endpoint direct** : `/fetch` récupère les contacts directement depuis Odoo
- **Endpoints sécurisés** : `/contacts` lit depuis la base de données

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

## Lancer l'API

```bash
# Lancer le serveur avec uvicorn
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible à :
- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc
- **Base URL** : http://localhost:8000

## Exécuter les tests

```bash
HMAC_SECRET="HMACsecretTest222@@" \
JWT_SECRET="JWTSEcret11@@" \
PYTHONPATH=./ \
uv run pytest tests/ -v -s
```

**Note** : L'option `-s` est requise pour afficher les `print()` dans les tests.

Les tests vérifient :
- Authentification et récupération des contacts
- Récupération d'un contact par ID
- Gestion des contacts non trouvés
- Rejet des identifiants invalides
- Rejet des requêtes sans JWT
- Rejet des requêtes sans signature HMAC

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
│   ├── install_cron.sh  # Script d'installation du cron
│   └── sync_with_env.sh # Sync avec chargement du .env
├── tests/
│   └── test_contacts.py # Tests
├── sync_contacts.py     # Script de synchronisation Odoo -> DB
├── init_db.py           # Initialisation de la base de données
├── crontab.example      # Exemple de configuration cron
├── pyproject.toml       # Configuration du projet et dépendances
├── requirements.txt     # Dépendances (utilisé par Vercel)
├── vercel.json          # Configuration Vercel
├── Dockerfile           # Image Docker
├── render.yaml          # Configuration Render.com
├── VERCEL_DEPLOY.md     # Guide de déploiement Vercel
└── README.md
```

## Développement

### Installer les dépendances de développement

```bash
uv sync --dev
```

### Tests

Les tests utilisent une base SQLite temporaire et surchargent la dépendance `get_db` de FastAPI pour isoler les tests de la base de production.

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

```bash
docker build -t odoo-contacts-api .
docker run -p 8000:8000 --env-file .env odoo-contacts-api
```

### Render.com

Le fichier `render.yaml` est fourni pour un déploiement sur Render. Les secrets JWT et HMAC sont générés automatiquement.
