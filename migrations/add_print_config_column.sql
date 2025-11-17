-- Migration: Ajout de la colonne print_config à la table suppliers
-- Date: 2025-11-13
-- Description: Ajoute une colonne JSONB pour stocker les paramètres d'impression de chaque fournisseur

-- Ajouter la colonne print_config (JSONB) avec une valeur par défaut
ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS print_config JSONB DEFAULT '{
  "columns_to_remove": [],
  "prefix_to_remove": "",
  "add_date": false,
  "paper_format": "A4"
}'::jsonb;

-- Commentaire pour documenter la colonne
COMMENT ON COLUMN suppliers.print_config IS 'Configuration d''impression: colonnes à supprimer, préfixe à retirer, ajout date, format papier';

-- Afficher un message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Colonne print_config ajoutée avec succès à la table suppliers';
END $$;
