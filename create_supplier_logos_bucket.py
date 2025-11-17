"""
Script pour créer le bucket supplier-logos dans Supabase Storage
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("CRÉATION DU BUCKET SUPPLIER-LOGOS")
print("=" * 60)
print()

# Connexion Supabase avec la clé service
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("[ERREUR] Variables d'environnement Supabase manquantes")
    exit(1)

supabase = create_client(supabase_url, supabase_key)
print("[OK] Connexion Supabase établie")
print()

try:
    # Créer le bucket supplier-logos (public)
    result = supabase.storage.create_bucket(
        'supplier-logos',
        options={'public': True}
    )

    print("[SUCCESS] Bucket 'supplier-logos' créé avec succès!")
    print("Le bucket est PUBLIC - les logos seront accessibles sans authentification")
    print()
    print("Prochaines étapes:")
    print("1. Allez dans Supabase Dashboard > Storage > supplier-logos")
    print("2. Uploadez vos logos (.jpg, .png, etc.)")
    print("3. Relancez l'application et ouvrez 'Gestion des Fournisseurs'")
    print("4. Les logos apparaîtront dans le sélecteur")

except Exception as e:
    error_message = str(e)
    if 'already exists' in error_message.lower():
        print("[INFO] Le bucket 'supplier-logos' existe déjà")
        print()
        print("Vérification de l'accès...")

        # Tester l'accès au bucket
        try:
            files = supabase.storage.from_('supplier-logos').list()
            print(f"[OK] {len(files)} fichier(s) trouvé(s) dans le bucket")

            if len(files) == 0:
                print()
                print("[INFO] Le bucket est vide")
                print("Uploadez vos logos dans Supabase Dashboard > Storage > supplier-logos")
            else:
                print()
                print("Fichiers trouvés:")
                for f in files:
                    print(f"  - {f.get('name')}")
        except Exception as e2:
            print(f"[ERREUR] Impossible d'accéder au bucket: {e2}")
    else:
        print(f"[ERREUR] {error_message}")
