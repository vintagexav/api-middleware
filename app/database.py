"""Configuration de la base de données."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# Chemin vers la base de données (PostgreSQL sur Vercel, SQLite en local)
DATABASE_URL = getattr(settings, "database_url", "sqlite:///./contacts.db")

# Configuration de l'engine selon le type de base de données
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    # Pour SQLite, désactiver le pool_pre_ping qui peut causer des problèmes
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=False,
    )
else:
    # PostgreSQL ou autre
    connect_args = {}
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,  # Vérifier la connexion avant utilisation
        pool_size=1,  # Limiter le pool pour serverless
        max_overflow=0,  # Pas de connexions supplémentaires
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency pour obtenir une session de base de données."""
    # S'assurer que les tables existent avant d'utiliser la DB
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # Log l'erreur mais continue (les tables existent peut-être déjà)
        print(f"Warning: Could not ensure tables exist: {e}")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
