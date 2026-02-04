# Odoo Contacts API

## Endpoints Vercel

Base URL : `https://api-middleware-two.vercel.app`

| Méthode | Endpoint | Auth | Description |
|---------|----------|------|-------------|
| `GET` | `/` | Non | Health check |
| `GET` | `/health` | Non | Health check détaillé (statut DB) |
| `GET` | `/fetched` | Non | Contacts récupérés en direct depuis Odoo |
| `POST` | `/auth/login` | Non | Obtenir un token JWT |
| `GET` | `/contacts` | JWT + HMAC | Contacts depuis la base de données locale |
| `GET` | `/contacts/{id}` | JWT + HMAC | Contact par ID depuis la base de données locale |

FastAPI proxy vers Odoo (contacts) avec authentification JWT + HMAC et synchronisation automatique.

## Description

Cette API middleware permet d'accéder aux contacts Odoo via une API REST sécurisée avec :
- **Synchronisation automatique** : Un cron job synchronise périodiquement les contacts depuis Odoo vers une base de données SQLite
- **Base de données locale** : Les contacts sont stockés localement pour des performances optimales
- **Authentification JWT** (JSON Web Tokens)
- **Vérification HMAC** pour l'intégrité des requêtes
- **API REST** pour récupérer les contacts depuis la base de données locale

## Prérequis

- Python >= 3.14
- `uv` (gestionnaire de paquets Python)
- Accès à une instance Odoo (pour la synchronisation)
- `cron` (pour la synchronisation automatique)

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

# Base de données (optionnel, par défaut: sqlite:///./contacts.db)
DATABASE_URL=sqlite:///./contacts.db
```

## Synchronisation des contacts

Avant de lancer l'API, vous devez synchroniser les contacts depuis Odoo vers la base de données locale.

### Synchronisation manuelle

```bash
# Synchroniser une fois les contacts depuis Odoo
uv run python sync_contacts.py
```

### Synchronisation automatique (Cron)

Pour synchroniser automatiquement les contacts toutes les 5 minutes :

#### Option 1 : Script d'installation automatique

```bash
# Installer le cron job automatiquement
./scripts/install_cron.sh
```

#### Option 2 : Installation manuelle

1. Éditez le fichier `crontab.example` et ajustez les chemins
2. Installez-le avec : `crontab crontab.example`
3. Vérifiez avec : `crontab -l`

#### Option 3 : Créer manuellement l'entrée cron

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne (ajustez les chemins selon votre installation)
*/5 * * * * cd /chemin/vers/api-middleware && /chemin/vers/uv run python sync_contacts.py >> /var/log/contacts_sync.log 2>&1
```

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

**Important** : L'API lit maintenant les contacts depuis la base de données locale, pas directement depuis Odoo. Assurez-vous d'avoir synchronisé les contacts au moins une fois avant d'utiliser l'API.

## Exécuter les tests

Pour exécuter les tests, utilisez la commande suivante :

```bash
HMAC_SECRET="HMACsecretTest222@@" \
JWT_SECRET="JWTSEcret11@@" \
PYTHONPATH=./ \
uv run pytest tests/ -v -s
```

**Important** : L'option `-s` (ou `--capture=no`) est **requise** pour afficher les `print()` dans vos tests. Sans cette option, pytest capture la sortie standard et les `print()` ne seront pas visibles.

Les tests vérifient :
- ✅ Authentification et récupération des contacts
- ✅ Récupération d'un contact par ID
- ✅ Gestion des contacts non trouvés
- ✅ Rejet des identifiants invalides
- ✅ Rejet des requêtes sans JWT
- ✅ Rejet des requêtes sans signature HMAC

## Endpoints API

### POST `/auth/login`
Authentification pour obtenir un token JWT.

**Body (form-data)**:
- `username`: Nom d'utilisateur
- `password`: Mot de passe

**Réponse**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### GET `/contacts`
Récupère tous les contacts depuis la base de données locale.

**Headers requis**:
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Réponse**:
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
Récupère un contact spécifique par ID depuis la base de données locale.

**Headers requis**:
- `Authorization: Bearer <token>`
- `X-Timestamp: <timestamp_unix>`
- `X-Signature: <hmac_signature>`

**Réponse**:
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
Chaque requête (sauf `/auth/login`) doit inclure :
- `X-Timestamp`: Timestamp Unix de la requête
- `X-Signature`: Signature HMAC-SHA256 calculée comme suit :

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
│   ├── config.py        # Configuration (settings)
│   ├── database.py      # Configuration SQLAlchemy
│   ├── models.py        # Modèles de base de données (Contact)
│   ├── db_client.py     # Client pour lire depuis la DB
│   ├── odoo_client.py   # Client XML-RPC pour Odoo
│   └── security.py      # Authentification JWT + HMAC
├── scripts/
│   └── install_cron.sh  # Script d'installation du cron
├── sync_contacts.py      # Script de synchronisation Odoo -> DB
├── crontab.example      # Exemple de configuration cron
├── contacts.db          # Base de données SQLite (créée automatiquement)
├── tests/
│   └── test_contacts.py # Tests unitaires
├── pyproject.toml       # Configuration du projet
└── README.md           # Ce fichier
```

## Développement

### Installer les dépendances de développement

```bash
uv sync --dev
```

### Tests

Les tests utilisent un `DummyOdooClient` pour éviter de nécessiter une connexion Odoo réelle. Voir la section "Exécuter les tests" ci-dessus.

## Architecture

### Flux de synchronisation

1. **Cron job** exécute `sync_contacts.py` périodiquement (par défaut toutes les 5 minutes)
2. **Script de synchronisation** :
   - Se connecte à Odoo via XML-RPC
   - Récupère tous les contacts
   - Synchronise la base de données locale :
     - **Insère** les nouveaux contacts
     - **Met à jour** les contacts existants
     - **Supprime** les contacts qui n'existent plus dans Odoo
3. **API FastAPI** lit les contacts depuis la base de données locale (pas directement depuis Odoo)

### Avantages

- ✅ **Performances** : Lecture rapide depuis la base de données locale
- ✅ **Fiabilité** : L'API fonctionne même si Odoo est temporairement indisponible
- ✅ **Synchronisation automatique** : Les contacts sont toujours à jour grâce au cron
- ✅ **Sécurité** : Pas d'accès direct à Odoo depuis l'API publique

## Déploiement

### Vercel

Pour déployer sur Vercel, consultez le guide détaillé : [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)

**Déploiement rapide :**
1. Installez Vercel CLI : `npm i -g vercel`
2. Configurez les variables d'environnement dans Vercel
3. Déployez : `vercel --prod`

⚠️ **Important** : SQLite ne fonctionne pas bien sur Vercel (serverless). Utilisez une base de données externe comme PostgreSQL.
