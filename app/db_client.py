"""Client pour accéder aux contacts depuis la base de données."""
from sqlalchemy.orm import Session

from .models import Contact


class DBClient:
    """Client pour lire les contacts depuis la base de données."""

    def __init__(self, db: Session):
        self.db = db

    def get_contacts(self):
        """Récupère tous les contacts depuis la base de données."""
        contacts = self.db.query(Contact).all()
        return [contact.to_dict() for contact in contacts]

    def get_contact_by_id(self, contact_id: int):
        """Récupère un contact par ID depuis la base de données."""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        return contact.to_dict() if contact else None
