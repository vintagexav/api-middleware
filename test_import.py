#!/usr/bin/env python3
"""Test d'import pour vérifier que tout fonctionne."""
import os
import sys

# Simuler l'environnement Vercel
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("HMAC_SECRET", "test-secret")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")

# Ajouter le répertoire parent au path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing imports...")
try:
    print("1. Importing mangum...")
    from mangum import Mangum
    print("   ✓ Mangum imported")
    
    print("2. Importing app.main...")
    from app.main import app
    print("   ✓ App imported")
    
    print("3. Creating Mangum handler...")
    handler = Mangum(app, lifespan="auto")
    print("   ✓ Handler created")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
