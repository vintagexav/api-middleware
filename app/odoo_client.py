import xmlrpc.client

from .config import settings


class OdooClient:
    def __init__(self) -> None:
        missing = [
            name
            for name, value in {
                "ODOO_URL": settings.odoo_url,
                "ODOO_DB": settings.odoo_db,
                "ODOO_USER": settings.odoo_user,
                "ODOO_PASSWORD": settings.odoo_password,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Variables d'environnement Odoo manquantes: "
                + ", ".join(missing)
                + ". Ajoute-les dans ton shell ou dans un fichier .env."
            )

        self.common = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(
            settings.odoo_db,
            settings.odoo_user,
            settings.odoo_password,
            {},
        )
        if not self.uid:
            raise RuntimeError("Échec d'authentification Odoo")
        self.models = xmlrpc.client.ServerProxy(f"{settings.odoo_url}/xmlrpc/2/object")

    def get_contacts(self):
        """Récupère tous les contacts (res.partner) selon la doc Odoo.
        
        Note: Le champ 'id' est toujours inclus même si non explicitement demandé.
        """
        return self.models.execute_kw(
            settings.odoo_db,
            self.uid,
            settings.odoo_password,
            "res.partner",
            "search_read",
            [[]],  # Domaine vide = tous les enregistrements
            {"fields": ["name", "email", "phone"]},  # 'id' est toujours inclus
        )

    def get_contact_by_id(self, contact_id: int):
        """Récupère un contact par ID selon la doc Odoo.
        
        Note: Le format correct est [ids] où ids est une liste d'IDs.
        Le champ 'id' est toujours inclus même si non explicitement demandé.
        """
        result = self.models.execute_kw(
            settings.odoo_db,
            self.uid,
            settings.odoo_password,
            "res.partner",
            "read",
            [[contact_id]],  # Format: liste contenant une liste d'IDs
            {"fields": ["name", "email", "phone"]},  # 'id' est toujours inclus
        )
        return result[0] if result else None

