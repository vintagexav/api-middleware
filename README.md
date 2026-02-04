# Odoo Contacts API

## Endpoints

Base URL (Vercel) : `https://api-middleware-two.vercel.app`

| Methode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/` | Non | Health check |
| `GET` | `/health` | Non | Health check detaille (statut DB) |
| `GET` | `/fetched` | Non | Contacts recuperes en direct depuis Odoo |
| `POST` | `/auth/login` | Non | Obtenir un token JWT |
| `GET` | `/contacts` | JWT + HMAC | Contacts depuis la base de donnees |
| `GET` | `/contacts/{id}` | JWT + HMAC | Contact par ID depuis la base de donnees |

FastAPI proxy vers Odoo (contacts) avec authentification JWT + HMAC.

## Description

Cette API middleware permet d'acceder aux contacts Odoo via une API REST securisee avec :
- **Authentification JWT** (JSON Web Tokens)
- **Verification HMAC** pour l'integrite des requetes
- **Base de donnees** : SQLite en dev local, PostgreSQL en production (Vercel)
- **Endpoint direct** : `/fetched` recupere les contacts directement depuis Odoo
- **Endpoints securises** : `/contacts` lit depuis la base de donnees

## Prerequis

- Python >= 3.12
- `uv` (gestionnaire de paquets Python)
- Acces a une instance Odoo

## Installation

```bash
# Installer les dependances avec uv
uv sync
```

## Configuration

Creez un fichier `.env` a la racine du projet avec les variables suivantes :

```env
# Configuration Odoo
ODOO_URL=http://your-odoo-instance.com
ODOO_DB=your_database
ODOO_USER=your_username
ODOO_PASSWORD=your_password

# Securite
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRE_MINUTES=60
HMAC_SECRET=your-hmac-secret-key

# Authentification de demo
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Base de donnees
# SQLite pour le developpement local (par defaut)
DATABASE_URL=sqlite:///./contacts.db
# PostgreSQL pour la production (Vercel, Render, etc.)
# DATABASE_URL=postgresql://user:password@host:5432/dbname
```

## Synchronisation des contacts (dev local)

En developpement local avec SQLite, vous pouvez synchroniser les contacts depuis Odoo vers la base de donnees.

> **Note** : Cette synchronisation par cron est prevue pour un serveur persistant. Sur Vercel (serverless), utilisez l'endpoint `/fetched` ou une base PostgreSQL alimentee autrement.

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

1. Editez le fichier `crontab.example` et ajustez les chemins
2. Installez-le avec : `crontab crontab.example`
3. Verifiez avec : `crontab -l`

**Note** : La synchronisation cree automatiquement la base de donnees et les tables si elles n'existent pas.

## Lancer l'API

```bash
# Lancer le serveur avec uvicorn
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible a :
- **Documentation interactive** : http://localhost:8000/docs
- **Documentation alternative** : http://localhost:8000/redoc
- **Base URL** : http://localhost:8000

## Executer les tests

```bash
HMAC_SECRET="HMACsecretTest222@@" \
JWT_SECRET="JWTSEcret11@@" \
PYTHONPATH=./ \
uv run pytest tests/ -v -s
```

**Note** : L'option `-s` est requise pour afficher les `print()` dans les tests.

Les tests verifient :
- Authentification et recuperation des contacts
- Recuperation d'un contact par ID
- Gestion des contacts non trouves
- Rejet des identifiants invalides
- Rejet des requetes sans JWT
- Rejet des requetes sans signature HMAC

## Endpoints API

### POST `/auth/login`
Authentification pour obtenir un token JWT.

**Body (form-data)**:
- `username`: Nom d'utilisateur
- `password`: Mot de passe

**Reponse**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET `/contacts`
Recupere tous les contacts depuis la base de donnees.

**Headers requis**:
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Reponse**:
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
Recupere un contact specifique par ID.

**Headers requis**:
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Reponse**:
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "123456789"
}
```

## Securite

### JWT (JSON Web Tokens)
- Utilise pour authentifier les utilisateurs
- Obtenu via `/auth/login`
- Inclus dans le header `Authorization: Bearer <token>`

### HMAC Signature
Chaque requete protegee (`/contacts`) doit inclure :
- `X-Timestamp`: Timestamp Unix de la requete
- `X-Signature`: Signature HMAC-SHA256 calculee comme suit :

```
message = method + path + timestamp + body
signature = HMAC-SHA256(hmac_secret, message)
```

La signature doit etre calculee avec le secret `HMAC_SECRET` configure.

## Structure du projet

```
api-middleware/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application FastAPI principale
│   ├── config.py        # Configuration (pydantic-settings)
│   ├── database.py      # Configuration SQLAlchemy
│   ├── models.py        # Modeles de base de donnees (Contact)
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
├── init_db.py           # Initialisation de la base de donnees
├── crontab.example      # Exemple de configuration cron
├── pyproject.toml       # Configuration du projet et dependances
├── requirements.txt     # Dependances (utilise par Vercel)
├── vercel.json          # Configuration Vercel
├── Dockerfile           # Image Docker
├── render.yaml          # Configuration Render.com
├── VERCEL_DEPLOY.md     # Guide de deploiement Vercel
└── README.md
```

## Developpement

### Installer les dependances de developpement

```bash
uv sync --dev
```

### Tests

Les tests utilisent une base SQLite temporaire et overrident la dependance `get_db` de FastAPI pour isoler les tests de la base de production.

## Architecture

### Deux modes d'acces aux contacts

1. **Direct** (`/fetched`) : Appel XML-RPC a Odoo en temps reel
2. **Via base de donnees** (`/contacts`) : Lecture depuis SQLite/PostgreSQL, alimentee par `sync_contacts.py`

### Flux de synchronisation (dev local)

1. `sync_contacts.py` se connecte a Odoo via XML-RPC
2. Recupere tous les contacts
3. Synchronise la base de donnees :
   - **Insere** les nouveaux contacts
   - **Met a jour** les contacts existants
   - **Supprime** les contacts qui n'existent plus dans Odoo
4. L'API lit les contacts depuis la base de donnees

## Deploiement

### Vercel (production)

Pour deployer sur Vercel, consultez le guide detaille : [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)

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

Le fichier `render.yaml` est fourni pour un deploiement sur Render. Les secrets JWT et HMAC sont generes automatiquement.
