"""
Script de migration pour créer la table app_settings
"""

import sys
from pathlib import Path
from loguru import logger

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_client import supabase_client


def run_migration():
    """Exécute la migration pour créer la table app_settings"""

    logger.info("=" * 60)
    logger.info("Migration: Création de la table app_settings")
    logger.info("=" * 60)

    # Lire le fichier SQL
    sql_file = Path(__file__).parent / "create_app_settings_table.sql"

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_query = f.read()

    try:
        # Exécuter la requête SQL via Supabase
        # Note: Cette méthode nécessite les permissions appropriées
        logger.info("Exécution du script SQL...")

        # Pour Supabase, il faut exécuter le SQL directement via l'interface web
        # ou utiliser l'API REST avec les bonnes permissions
        logger.warning("⚠️  Cette migration doit être exécutée manuellement dans Supabase:")
        logger.info("1. Allez sur https://supabase.com/dashboard")
        logger.info("2. Sélectionnez votre projet")
        logger.info("3. Allez dans SQL Editor")
        logger.info(f"4. Collez et exécutez le contenu de {sql_file.name}")

        print("\n" + "="*60)
        print("SCRIPT SQL À EXÉCUTER DANS SUPABASE:")
        print("="*60)
        print(sql_query)
        print("="*60)

        return True

    except Exception as e:
        logger.error(f"❌ Erreur lors de la migration: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
