"""Modèles de base de données pour les contacts."""
from sqlalchemy import Column, Integer, String

from .database import Base


class Contact(Base):
    """Modèle pour les contacts synchronisés depuis Odoo."""

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)  # ID Odoo
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    def to_dict(self):
        """Convertit le modèle en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }
