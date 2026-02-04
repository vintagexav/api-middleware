#!/usr/bin/env python3
"""Script complet pour tester les appels API à Odoo (direct et via FastAPI)"""

import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# Ajouter le répertoire racine du projet au path (deux niveaux au-dessus)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from app.odoo_client import OdooClient


def test_direct_odoo():
    """Teste les appels directs à Odoo via XML-RPC."""
    print("=" * 70)
    print("TEST 1: Appels directs à Odoo (XML-RPC)")
    print("=" * 70)
    print()

    try:
        print("1️⃣  Connexion à Odoo...")
        odoo = OdooClient()
        print(f"✅ Connexion réussie! UID: {odoo.uid}")
        print()

        print("2️⃣  Récupération de tous les contacts...")
        contacts = odoo.get_contacts()
        print(f"✅ {len(contacts)} contact(s) récupéré(s)")
        print()

        if contacts:
            print("3️⃣  Détails des contacts:")
            print("-" * 70)
            for i, contact in enumerate(contacts, 1):
                print(f"\nContact #{i}:")
                print(f"  ID: {contact.get('id', 'N/A')}")
                print(f"  Nom: {contact.get('name', 'N/A')}")
                print(f"  Email: {contact.get('email', 'N/A')}")
                print(f"  Téléphone: {contact.get('phone', 'N/A')}")
            print()

            # Test récupération d'un contact par ID
            first_contact_id = contacts[0].get('id')
            if first_contact_id:
                print(f"4️⃣  Récupération du contact ID {first_contact_id}...")
                contact = odoo.get_contact_by_id(first_contact_id)
                if contact:
                    print("✅ Contact récupéré:")
                    print(json.dumps(contact, indent=2, ensure_ascii=False))
                else:
                    print(f"❌ Contact ID {first_contact_id} non trouvé")
                print()

        print("✅ Test direct Odoo réussi!")
        return True

    except RuntimeError as e:
        print(f"❌ Erreur de configuration: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à Odoo: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fastapi_endpoint(api_url="http://127.0.0.1:8000"):
    """Teste l'endpoint /fetch de l'API FastAPI."""
    print()
    print("=" * 70)
    print("TEST 2: Appels via FastAPI (/fetch endpoint)")
    print("=" * 70)
    print()

    try:
        print(f"1️⃣  Test de l'endpoint {api_url}/fetch...")
        req = Request(f"{api_url}/fetch")
        
        with urlopen(req, timeout=10) as resp:
            contacts = json.loads(resp.read())
            print(f"✅ {len(contacts)} contact(s) récupéré(s) via l'API")
            print()

            if contacts:
                print("2️⃣  Détails des contacts:")
                print("-" * 70)
                for i, contact in enumerate(contacts[:5], 1):  # Afficher les 5 premiers
                    print(f"\nContact #{i}:")
                    print(f"  ID: {contact.get('id', 'N/A')}")
                    print(f"  Nom: {contact.get('name', 'N/A')}")
                    print(f"  Email: {contact.get('email', 'N/A')}")
                    print(f"  Téléphone: {contact.get('phone', 'N/A')}")
                
                if len(contacts) > 5:
                    print(f"\n... et {len(contacts) - 5} autre(s) contact(s)")
                print()

        print("✅ Test FastAPI réussi!")
        return True

    except HTTPError as e:
        print(f"❌ Erreur HTTP {e.code}: {e.reason}")
        try:
            error_body = e.read().decode()
            print(f"Body: {error_body}")
        except:
            pass
        print("\n💡 Assurez-vous que le serveur FastAPI est démarré:")
        print("   ./scripts/run_server.sh")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à l'API: {e}")
        print("\n💡 Assurez-vous que le serveur FastAPI est démarré:")
        print("   ./scripts/run_server.sh")
        return False


def main():
    """Exécute tous les tests."""
    print()
    print("🚀 Tests des appels API à Odoo")
    print()

    # Test 1: Appels directs
    success_direct = test_direct_odoo()

    # Test 2: Via FastAPI (si le serveur est démarré)
    print()
    print("⏳ Attente de 2 secondes avant le test FastAPI...")
    time.sleep(2)
    success_api = test_fastapi_endpoint()

    # Résumé
    print()
    print("=" * 70)
    print("RÉSUMÉ DES TESTS")
    print("=" * 70)
    print(f"✅ Appels directs Odoo: {'✅ Réussi' if success_direct else '❌ Échec'}")
    print(f"✅ Endpoint FastAPI /fetch: {'✅ Réussi' if success_api else '❌ Échec (serveur non démarré?)'}")
    print("=" * 70)
    print()

    if success_direct:
        print("✅ Les appels API à Odoo fonctionnent correctement!")
    else:
        print("❌ Vérifiez votre configuration Odoo dans le fichier .env")
        sys.exit(1)


if __name__ == "__main__":
    main()
