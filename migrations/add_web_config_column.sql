-- Migration: Ajout de la colonne web_config à la table suppliers
-- Date: 2025-01-14
-- Description: Ajoute la colonne JSONB web_config pour stocker les paramètres de connexion web automatique

-- Ajouter la colonne web_config si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'suppliers'
        AND column_name = 'web_config'
    ) THEN
        ALTER TABLE suppliers
        ADD COLUMN web_config JSONB DEFAULT '{}'::jsonb;

        RAISE NOTICE 'Colonne web_config ajoutée avec succès';
    ELSE
        RAISE NOTICE 'La colonne web_config existe déjà';
    END IF;
END $$;

-- Vérification
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'suppliers'
AND column_name = 'web_config';
