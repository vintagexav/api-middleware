#!/usr/bin/env python3
"""Script de synchronisation des contacts depuis Odoo vers la base de données.

Ce script récupère tous les contacts depuis Odoo et les synchronise dans la base
de données locale (insertion, mise à jour, suppression).
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Base, Contact
from app.odoo_client import OdooClient


def sync_contacts():
    """Synchronise les contacts depuis Odoo vers la base de données."""
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        print("🔄 Connexion à Odoo...")
        odoo_client = OdooClient()

        print("📥 Récupération des contacts depuis Odoo...")
        odoo_contacts = odoo_client.get_contacts()
        print(f"✅ {len(odoo_contacts)} contacts récupérés depuis Odoo")

        # Récupérer tous les IDs Odoo existants dans la DB
        existing_ids = {contact.id for contact in db.query(Contact.id).all()}
        odoo_ids = {contact["id"] for contact in odoo_contacts}

        # Contacts à supprimer (dans DB mais plus dans Odoo)
        to_delete_ids = existing_ids - odoo_ids
        if to_delete_ids:
            print(f"🗑️  Suppression de {len(to_delete_ids)} contacts...")
            db.query(Contact).filter(Contact.id.in_(to_delete_ids)).delete(
                synchronize_session=False
            )

        # Contacts à insérer ou mettre à jour
        inserted_count = 0
        updated_count = 0

        for odoo_contact in odoo_contacts:
            contact_id = odoo_contact["id"]
            existing_contact = db.query(Contact).filter(Contact.id == contact_id).first()

            if existing_contact:
                # Mise à jour
                existing_contact.name = odoo_contact.get("name")
                existing_contact.email = odoo_contact.get("email")
                existing_contact.phone = odoo_contact.get("phone")
                updated_count += 1
            else:
                # Insertion
                new_contact = Contact(
                    id=contact_id,
                    name=odoo_contact.get("name"),
                    email=odoo_contact.get("email"),
                    phone=odoo_contact.get("phone"),
                )
                db.add(new_contact)
                inserted_count += 1

        db.commit()
        print(f"✅ Synchronisation terminée:")
        print(f"   - {inserted_count} contacts insérés")
        print(f"   - {updated_count} contacts mis à jour")
        print(f"   - {len(to_delete_ids)} contacts supprimés")
        print(f"   - Total: {len(odoo_contacts)} contacts dans la base")

    except Exception as exc:
        db.rollback()
        print(f"❌ Erreur lors de la synchronisation: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    sync_contacts()
