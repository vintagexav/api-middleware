# Scripts de test manuels

Ce dossier contient des scripts de test manuels pour tester l'API de différentes manières.

## Scripts Python

### `test_api.py`
Script de test basique pour tester l'API locale avec calcul HMAC correct.

**Usage:**
```bash
python3 tests/scripts/test_api.py
```

### `test_api_improved.py`
Version améliorée avec meilleure gestion d'erreurs.

**Usage:**
```bash
python3 tests/scripts/test_api_improved.py
```

### `test_vercel.py`
Script pour tester l'API déployée sur Vercel.

**Usage:**
```bash
python3 tests/scripts/test_vercel.py
```

### `test_vercel_debug.py`
Version de debug avec affichage détaillé pour tester l'API Vercel.

**Usage:**
```bash
python3 tests/scripts/test_vercel_debug.py
```

### `test_import.py`
Test d'import pour vérifier que tous les modules peuvent être importés correctement (utile pour Vercel).

**Usage:**
```bash
python3 tests/scripts/test_import.py
```

## Scripts Shell

### `test_api.sh`
Script bash pour tester l'API locale avec curl.

**Usage:**
```bash
./tests/scripts/test_api.sh
```

### `test_vercel.sh`
Script bash pour tester l'API Vercel avec curl.

**Usage:**
```bash
./tests/scripts/test_vercel.sh
```

## Note

Ces scripts sont des outils de test manuels et ne font pas partie de la suite de tests automatisés. Pour exécuter les tests unitaires, utilisez :

```bash
./scripts/run_tests.sh
```
