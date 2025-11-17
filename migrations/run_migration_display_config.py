"""
Script de migration pour ajouter la colonne display_config à la table suppliers
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_client import supabase_client
from loguru import logger


def run_migration():
    """Exécute la migration pour ajouter display_config"""
    try:
        # Lire le fichier SQL
        sql_file = Path(__file__).parent / 'add_display_config_column.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        logger.info("Exécution de la migration display_config...")
        logger.info(f"Contenu SQL:\n{sql_content}")

        # Exécuter la migration
        result = supabase_client.client.rpc('exec_sql', {'query': sql_content}).execute()

        logger.success("✅ Migration display_config exécutée avec succès!")
        logger.info(f"Résultat: {result}")

        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Migration: Ajout de la colonne display_config")
    print("=" * 60)

    success = run_migration()

    if success:
        print("\n✅ Migration terminée avec succès!")
    else:
        print("\n❌ Échec de la migration")
        sys.exit(1)
