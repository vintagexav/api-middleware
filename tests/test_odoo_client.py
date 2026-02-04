#!/usr/bin/env python3
"""Tests pour le client Odoo (XML-RPC)"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.odoo_client import OdooClient
from app.config import settings


def test_odoo_client_initialization():
    """Teste l'initialisation du client Odoo."""
    # Vérifier que les variables d'environnement sont définies
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    # Créer le client
    client = OdooClient()
    
    # Vérifier que le client est initialisé
    assert client is not None
    assert client.uid is not None
    assert client.common is not None
    assert client.models is not None


def test_get_contacts():
    """Teste la récupération de tous les contacts."""
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    client = OdooClient()
    contacts = client.get_contacts()
    
    # Vérifier que c'est une liste
    assert isinstance(contacts, list)
    
    # Si des contacts existent, vérifier leur structure
    if contacts:
        contact = contacts[0]
        assert "id" in contact
        assert "name" in contact
        # email et phone peuvent être None
        assert "email" in contact
        assert "phone" in contact


def test_get_contact_by_id():
    """Teste la récupération d'un contact par ID."""
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    client = OdooClient()
    
    # D'abord récupérer tous les contacts pour avoir un ID valide
    contacts = client.get_contacts()
    
    if not contacts:
        pytest.skip("Aucun contact dans Odoo pour tester")
    
    # Récupérer le premier contact par ID
    first_contact_id = contacts[0]["id"]
    contact = client.get_contact_by_id(first_contact_id)
    
    # Vérifier que le contact est récupéré
    assert contact is not None
    assert contact["id"] == first_contact_id
    assert "name" in contact
    assert "email" in contact
    assert "phone" in contact


def test_get_contact_by_id_not_found():
    """Teste la récupération d'un contact avec un ID inexistant."""
    if not all([settings.odoo_url, settings.odoo_db, settings.odoo_user, settings.odoo_password]):
        pytest.skip("Variables d'environnement Odoo non configurées")
    
    client = OdooClient()
    
    # Utiliser un ID très grand qui n'existe probablement pas
    contact = client.get_contact_by_id(999999999)
    
    # Devrait retourner None pour un ID inexistant
    assert contact is None


def test_odoo_client_missing_env_vars():
    """Teste que le client lève une erreur si les variables d'environnement manquent."""
    # Sauvegarder les valeurs actuelles
    original_url = settings.odoo_url
    original_db = settings.odoo_db
    original_user = settings.odoo_user
    original_password = settings.odoo_password
    
    try:
        # Désactiver temporairement une variable
        settings.odoo_url = None
        
        # Devrait lever une RuntimeError
        with pytest.raises(RuntimeError, match="Variables d'environnement Odoo manquantes"):
            OdooClient()
    finally:
        # Restaurer les valeurs
        settings.odoo_url = original_url
        settings.odoo_db = original_db
        settings.odoo_user = original_user
        settings.odoo_password = original_password
