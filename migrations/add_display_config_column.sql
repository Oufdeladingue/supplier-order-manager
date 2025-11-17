-- Migration: Ajout de la colonne display_config à la table suppliers
-- Date: 2025-01-14
-- Description: Ajoute la colonne JSONB display_config pour stocker les paramètres d'affichage (bouton Ouvrir)

-- Ajouter la colonne display_config si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'suppliers'
        AND column_name = 'display_config'
    ) THEN
        ALTER TABLE suppliers
        ADD COLUMN display_config JSONB DEFAULT '{}'::jsonb;

        RAISE NOTICE 'Colonne display_config ajoutée avec succès';
    ELSE
        RAISE NOTICE 'La colonne display_config existe déjà';
    END IF;
END $$;

-- Vérification
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'suppliers'
AND column_name = 'display_config';
