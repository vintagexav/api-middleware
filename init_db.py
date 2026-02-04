#!/usr/bin/env python3
"""Script pour initialiser la base de données (créer les tables)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import Base, engine
from app.models import Contact

if __name__ == "__main__":
    print("🔄 Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès!")
    print(f"   - Table: {Contact.__tablename__}")
