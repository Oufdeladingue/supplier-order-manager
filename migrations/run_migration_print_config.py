"""
Script de migration pour ajouter la colonne print_config à la table suppliers
"""

import sys
from pathlib import Path
from loguru import logger

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_client import supabase_client


def run_migration():
    """Exécute la migration pour ajouter print_config"""

    logger.info("=" * 60)
    logger.info("Migration: Ajout de la colonne print_config")
    logger.info("=" * 60)

    sql_query = """
    -- Ajouter la colonne print_config (JSONB) avec une valeur par défaut
    ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS print_config JSONB DEFAULT '{
      "columns_to_remove": [],
      "prefix_to_remove": "",
      "add_date": false,
      "paper_format": "A4"
    }'::jsonb;
    """

    try:
        # Exécuter la requête SQL via Supabase
        result = supabase_client.client.rpc('exec_sql', {'sql': sql_query}).execute()

        logger.success("✅ Colonne print_config ajoutée avec succès!")

        # Vérifier que la colonne a bien été ajoutée
        test_query = supabase_client.client.table('suppliers').select('id, name, print_config').limit(1).execute()

        if test_query.data:
            logger.info(f"✅ Vérification: {len(test_query.data)} fournisseur(s) trouvé(s) avec print_config")
            logger.info(f"   Exemple: {test_query.data[0]}")
        else:
            logger.warning("⚠️ Aucun fournisseur trouvé pour tester la nouvelle colonne")

        logger.success("Migration terminée avec succès!")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {e}")
        logger.info("Si la fonction exec_sql n'existe pas, vous devez exécuter le SQL manuellement dans Supabase:")
        logger.info("1. Allez sur https://supabase.com/dashboard")
        logger.info("2. Sélectionnez votre projet")
        logger.info("3. Allez dans SQL Editor")
        logger.info("4. Collez et exécutez le contenu de migrations/add_print_config_column.sql")
        return False

    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
