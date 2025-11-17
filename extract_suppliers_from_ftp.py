"""
Script pour extraire la liste des fournisseurs depuis les fichiers FTP
et les créer automatiquement dans la base de données
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from worker.ftp_fetcher import FTPFetcher
from loguru import logger

# Fix encoding pour Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("=" * 60)
print("EXTRACTION DES FOURNISSEURS DEPUIS FTP")
print("=" * 60)
print()

# Connexion Supabase avec la clé service pour bypasser RLS
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Utiliser la clé service

if not supabase_url or not supabase_key:
    print("[ERREUR] Variables d'environnement Supabase manquantes")
    print("[INFO] Assurez-vous que SUPABASE_URL et SUPABASE_SERVICE_KEY sont définis dans .env")
    exit(1)

supabase = create_client(supabase_url, supabase_key)
print("[OK] Connexion Supabase établie")
print()

# Connexion FTP
ftp_host = os.getenv("FTP_HOST")
ftp_port = int(os.getenv("FTP_PORT", 22))
ftp_user = os.getenv("FTP_USERNAME")
ftp_pass = os.getenv("FTP_PASSWORD")
ftp_path = os.getenv("FTP_REMOTE_PATH", "/home/mjard_ep43/export-cdes-fournisseurs")

if not all([ftp_host, ftp_user, ftp_pass]):
    print("[ERREUR] Configuration FTP incomplète")
    exit(1)

print(f"[INFO] Connexion au serveur FTP {ftp_host}...")
fetcher = FTPFetcher(ftp_host, ftp_port, ftp_user, ftp_pass, use_sftp=True)
fetcher.connect()

# Récupérer la liste des fichiers
files = fetcher.list_files(ftp_path, exclude_dirs=['old'])
fetcher.disconnect()

print(f"[OK] {len(files)} fichier(s) trouvé(s)")
print()

# Extraire les noms de fournisseurs depuis les noms de fichiers
# Format attendu: "Nom Fournisseur-DD-MM-YY.csv"
suppliers_found = {}

for file_info in files:
    filename = file_info['filename']

    # Extraire le nom du fournisseur (tout ce qui est avant le premier "-")
    match = re.match(r'^([^-]+)-', filename)
    if match:
        supplier_name = match.group(1).strip()

        if supplier_name not in suppliers_found:
            suppliers_found[supplier_name] = {
                'name': supplier_name,
                'file_count': 0,
                'example_files': []
            }

        suppliers_found[supplier_name]['file_count'] += 1
        if len(suppliers_found[supplier_name]['example_files']) < 3:
            suppliers_found[supplier_name]['example_files'].append(filename)

print(f"[INFO] {len(suppliers_found)} fournisseur(s) unique(s) détecté(s):")
print()

for supplier_name, info in sorted(suppliers_found.items()):
    print(f"  • {supplier_name}")
    print(f"    - {info['file_count']} fichier(s)")
    print(f"    - Exemples: {', '.join(info['example_files'][:2])}")
    print()

# Créer les fournisseurs dans la base de données
print("=" * 60)
print("CRÉATION DES FOURNISSEURS DANS LA BASE DE DONNÉES")
print("=" * 60)
print()

created = 0
skipped = 0
errors = 0

for supplier_name, info in sorted(suppliers_found.items()):
    # Générer un code unique à partir du nom
    supplier_code = supplier_name.lower().replace(' ', '_').replace('-', '_')

    print(f"Création: {supplier_name} (code: {supplier_code})...")

    try:
        # Vérifier si déjà existant
        existing = supabase.table('suppliers').select('id').eq('supplier_code', supplier_code).execute()

        if existing.data:
            print(f"  [SKIP] Fournisseur déjà existant")
            skipped += 1
            continue

        # Préparer les données
        data = {
            'supplier_code': supplier_code,
            'name': supplier_name,
            'file_filter_slug': supplier_name,  # Le slug de filtre est le nom complet par défaut
            'file_patterns': [f"{supplier_name}-*.csv"],
            'source': 'ftp',
            'ftp_path': ftp_path,
            'active': True,
            'import_config': {
                'output_format': 'xlsx',
                'has_header': False,
                'leading_zeros': False
            },
            'notes': f"Créé automatiquement depuis FTP. {info['file_count']} fichier(s) détecté(s)."
        }

        # Insérer dans Supabase
        result = supabase.table('suppliers').insert(data).execute()

        if result.data:
            print(f"  [OK] Créé avec succès")
            created += 1
        else:
            print(f"  [ERREUR] Échec insertion")
            errors += 1

    except Exception as e:
        print(f"  [ERREUR] {str(e)}")
        errors += 1

print()
print("=" * 60)
print("RÉSUMÉ")
print("=" * 60)
print(f"✅ Créés:  {created}")
print(f"⏭️  Ignorés: {skipped}")
print(f"❌ Erreurs: {errors}")
print()

if created > 0:
    print("[SUCCESS] Extraction terminée !")
    print()
    print("Prochaines étapes :")
    print("1. Ouvrez l'application et allez dans 'Gestion des fournisseurs'")
    print("2. Complétez les informations manquantes pour chaque fournisseur")
    print("3. Configurez les paramètres d'import dans l'onglet 'Import'")
else:
    print("[INFO] Aucun fournisseur créé")
    if skipped > 0:
        print("Les fournisseurs existent déjà dans la base")
