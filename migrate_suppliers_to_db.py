"""
Script de migration des fournisseurs depuis JSON vers Supabase
À exécuter une seule fois pour importer les données
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("MIGRATION FOURNISSEURS JSON → SUPABASE")
print("=" * 60)
print()

# Connexion Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("[ERREUR] Variables d'environnement Supabase manquantes")
    exit(1)

client = create_client(url, key)
print("[OK] Connexion Supabase établie")
print()

# Charger le fichier JSON
json_path = Path(__file__).parent / "config" / "suppliers.json"

if not json_path.exists():
    print(f"[ERREUR] Fichier {json_path} introuvable")
    exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

suppliers_json = config.get('suppliers', [])

print(f"[INFO] {len(suppliers_json)} fournisseur(s) trouvé(s) dans le JSON")
print()

# Migrer chaque fournisseur
migrated = 0
skipped = 0
errors = 0

for supplier in suppliers_json:
    supplier_code = supplier.get('id')
    name = supplier.get('name')

    print(f"Migration: {name} ({supplier_code})...")

    try:
        # Vérifier si déjà existant
        existing = client.table('suppliers').select('id').eq('supplier_code', supplier_code).execute()

        if existing.data:
            print(f"  [SKIP] Fournisseur déjà existant")
            skipped += 1
            continue

        # Préparer les données
        data = {
            'supplier_code': supplier_code,
            'name': name,
            'email_pattern': supplier.get('email_pattern'),
            'file_patterns': supplier.get('file_patterns', []),
            'source': supplier.get('source', 'ftp'),
            'ftp_path': supplier.get('ftp_path'),
            'transformation_id': supplier.get('transformation_id'),
            'min_order_amount': supplier.get('min_order', 0),
            'active': supplier.get('active', True),
            'notes': f"Importé depuis JSON le {os.popen('date /t').read().strip() if sys.platform == 'win32' else os.popen('date').read().strip()}"
        }

        # Insérer dans Supabase
        result = client.table('suppliers').insert(data).execute()

        if result.data:
            print(f"  [OK] Migré avec succès")
            migrated += 1
        else:
            print(f"  [ERREUR] Échec insertion")
            errors += 1

    except Exception as e:
        print(f"  [ERREUR] {str(e)}")
        errors += 1

print()
print("=" * 60)
print("RÉSUMÉ DE LA MIGRATION")
print("=" * 60)
print(f"✅ Migrés:  {migrated}")
print(f"⏭️  Ignorés:  {skipped}")
print(f"❌ Erreurs:  {errors}")
print()

if migrated > 0:
    print("[SUCCESS] Migration terminée !")
    print()
    print("Prochaines étapes :")
    print("1. Vérifiez les données dans Supabase")
    print("2. L'application utilisera désormais la BDD")
    print("3. Le fichier JSON peut être conservé comme backup")
else:
    print("[INFO] Aucune donnée migrée")
    if skipped > 0:
        print("Les fournisseurs existent déjà dans la base")
