"""
Script de migration pour ajouter la colonne web_config à la table suppliers
"""

import sys
from pathlib import Path
from loguru import logger

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_client import supabase_client


def run_migration():
    """Exécute la migration pour ajouter web_config"""

    logger.info("=" * 60)
    logger.info("Migration: Ajout de la colonne web_config")
    logger.info("=" * 60)

    sql_query = """
    -- Ajouter la colonne web_config (JSONB) avec une valeur par défaut
    ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS web_config JSONB DEFAULT '{
      "url": "",
      "client_code_enabled": false,
      "client_code_value": "",
      "client_code_selector": "",
      "login_value": "",
      "login_selector": "",
      "password_value": "",
      "password_selector": "",
      "other_enabled": false,
      "other_value": "",
      "other_selector": "",
      "submit_selector": "",
      "intermediate_enabled": false,
      "intermediate_selector": "",
      "cookie_enabled": false,
      "cookie_selector": "",
      "captcha_detect": false
    }'::jsonb;
    """

    try:
        # Exécuter la requête SQL via Supabase
        result = supabase_client.client.rpc('exec_sql', {'sql': sql_query}).execute()

        logger.success("Migration web_config executee avec succes!")

        # Vérifier que la colonne a bien été ajoutée
        test_query = supabase_client.client.table('suppliers').select('id, name, web_config').limit(1).execute()

        if test_query.data:
            logger.info(f"Verification: {len(test_query.data)} fournisseur(s) trouve(s) avec web_config")
            logger.info(f"   Exemple: {test_query.data[0]}")
        else:
            logger.warning("Aucun fournisseur trouve pour tester la nouvelle colonne")

        logger.success("Migration terminee avec succes!")

    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        logger.info("Si la fonction exec_sql n'existe pas, vous devez executer le SQL manuellement dans Supabase:")
        logger.info("1. Allez sur https://supabase.com/dashboard")
        logger.info("2. Selectionnez votre projet")
        logger.info("3. Allez dans SQL Editor")
        logger.info("4. Collez et executez le SQL suivant:")
        logger.info(sql_query)
        return False

    return True


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
