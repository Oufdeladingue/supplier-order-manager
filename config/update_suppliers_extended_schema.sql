-- Mise à jour du schéma de la table suppliers pour ajouter les informations étendues
-- Exécuter ce script dans Supabase SQL Editor

-- Colonnes d'informations de contact
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS phone TEXT;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS email TEXT;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS website TEXT;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS web_user TEXT;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS web_password TEXT;

-- Colonnes pour le filtre de fichiers
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS file_filter_slug TEXT;

-- Colonnes pour la configuration d'import (stockées en JSON pour flexibilité)
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS import_config JSONB DEFAULT '{}'::jsonb;

-- Mise à jour de la fonction de trigger (déjà existante, on la conserve)
-- Elle met à jour last_modified_at automatiquement

-- Index pour améliorer les performances de recherche
CREATE INDEX IF NOT EXISTS idx_suppliers_filter_slug ON suppliers(file_filter_slug);

-- Commentaires pour documentation
COMMENT ON COLUMN suppliers.phone IS 'Numéro de téléphone du fournisseur';
COMMENT ON COLUMN suppliers.email IS 'Adresse email du fournisseur';
COMMENT ON COLUMN suppliers.website IS 'Site web du fournisseur';
COMMENT ON COLUMN suppliers.web_user IS 'Identifiant pour accéder au site web du fournisseur';
COMMENT ON COLUMN suppliers.web_password IS 'Mot de passe pour accéder au site web du fournisseur';
COMMENT ON COLUMN suppliers.file_filter_slug IS 'Slug de filtre (premières lettres du nom de fichier pour filtrer les fichiers par fournisseur)';
COMMENT ON COLUMN suppliers.import_config IS 'Configuration d''import au format JSON: {"output_format": "xlsx|csv", "has_header": true|false, "leading_zeros": true|false}';

-- Exemple de structure pour import_config:
-- {
--   "output_format": "xlsx",
--   "has_header": true,
--   "leading_zeros": false
-- }
