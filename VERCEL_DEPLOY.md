# Déploiement sur Vercel

Ce guide explique comment déployer l'API Odoo Contacts sur Vercel.

## Prérequis 

1. Un compte Vercel (gratuit)
2. Le CLI Vercel installé : `npm i -g vercel`
3. Un compte GitHub (pour le déploiement automatique)

## Configuration

### 1. Variables d'environnement

Vous devez configurer les variables d'environnement suivantes dans Vercel :

**Obligatoires :**
- `ODOO_URL` - URL de votre instance Odoo
- `ODOO_DB` - Nom de la base de données Odoo
- `ODOO_USER` - Nom d'utilisateur Odoo
- `ODOO_PASSWORD` - Mot de passe Odoo

**Sécurité :**
- `JWT_SECRET` - Secret pour signer les tokens JWT
- `HMAC_SECRET` - Secret pour la vérification HMAC
- `JWT_EXPIRE_MINUTES` - Durée de validité des tokens (défaut: 60)

**Authentification :**
- `ADMIN_USERNAME` - Nom d'utilisateur pour l'authentification (défaut: admin)
- `ADMIN_PASSWORD` - Mot de passe pour l'authentification (défaut: admin)

**Base de données :**
- `DATABASE_URL` - URL de la base de données (optionnel, par défaut: sqlite:///./contacts.db)

⚠️ **Note importante sur SQLite** : SQLite n'est pas recommandé pour Vercel car les fonctions serverless sont éphémères. Utilisez plutôt une base de données externe comme :
- PostgreSQL (via Vercel Postgres, Supabase, ou Railway)
- MySQL (via PlanetScale ou autre)
- MongoDB (via MongoDB Atlas)

### 2. Configuration de la base de données

Pour utiliser PostgreSQL avec Vercel :

1. Créez une base de données PostgreSQL (Vercel Postgres, Supabase, etc.)
2. Configurez `DATABASE_URL` dans les variables d'environnement Vercel :
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```
3. Assurez-vous que SQLAlchemy peut se connecter à PostgreSQL (déjà inclus dans les dépendances)

## Déploiement

### Option 1 : Via le Dashboard Vercel (Recommandé)

1. Allez sur [vercel.com](https://vercel.com)
2. Cliquez sur "Add New Project"
3. Importez votre dépôt GitHub
4. Configurez les variables d'environnement dans les paramètres du projet
5. Cliquez sur "Deploy"

### Option 2 : Via le CLI Vercel

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter à Vercel
vercel login

# Déployer
vercel

# Pour la production
vercel --prod
```

### Option 3 : Déploiement automatique

Si vous avez connecté votre dépôt GitHub à Vercel, chaque push sur `main` déclenchera automatiquement un déploiement.

## Structure des fichiers Vercel

- `vercel.json` - Configuration Vercel
- `api/index.py` - Handler FastAPI pour Vercel
- `requirements.txt` - Dépendances Python
- `.vercelignore` - Fichiers à ignorer lors du déploiement

## Limitations Vercel

1. **Fonctions serverless** : Chaque requête est une nouvelle instance
2. **Timeout** : Maximum 30 secondes pour les fonctions (par défaut, configurable dans les paramètres du projet)
3. **Base de données** : SQLite ne fonctionne pas bien, utilisez une DB externe
4. **Cron jobs** : Vercel ne supporte pas les cron jobs natifs. Utilisez :
   - Vercel Cron Jobs (fonctionnalité payante)
   - Un service externe comme cron-job.org
   - GitHub Actions avec un workflow cron

## Synchronisation des contacts

Comme Vercel ne supporte pas les cron jobs natifs, vous avez plusieurs options :

### Option 1 : Vercel Cron Jobs (Payant)
Créez un fichier `api/cron/sync.py` et configurez-le dans Vercel.

### Option 2 : Service externe
Utilisez un service comme [cron-job.org](https://cron-job.org) pour appeler votre endpoint de synchronisation.

### Option 3 : GitHub Actions
Créez un workflow GitHub Actions qui synchronise périodiquement.

## Vérification du déploiement

Une fois déployé, votre API sera accessible à :
- `https://api-middleware-two.vercel.app`
- `https://api-middleware-two.vercel.app/docs` - Documentation interactive
- `https://api-middleware-two.vercel.app/redoc` - Documentation alternative

## Dépannage

### Erreur : "Module not found"
- Vérifiez que `requirements.txt` contient toutes les dépendances
- Vérifiez que les imports dans `api/index.py` sont corrects

### Erreur : "Database connection failed"
- Vérifiez que `DATABASE_URL` est correctement configuré
- Assurez-vous que la base de données est accessible depuis Internet
- Pour PostgreSQL, vérifiez les paramètres de sécurité/firewall

### Erreur : "Environment variable not found"
- Vérifiez que toutes les variables d'environnement sont configurées dans Vercel
- Redéployez après avoir ajouté de nouvelles variables

## Support

Pour plus d'informations, consultez la [documentation Vercel](https://vercel.com/docs).
