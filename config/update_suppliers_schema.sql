-- Mise à jour du schéma de la table suppliers
-- Ajouter les colonnes manquantes pour la configuration complète

-- Ajouter colonne minimum de commande
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS min_order_amount DECIMAL(10, 2) DEFAULT 0;

-- Ajouter colonne chemin FTP
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS ftp_path TEXT;

-- Ajouter colonne ID de transformation
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS transformation_id TEXT;

-- Ajouter colonne logo (URL ou chemin)
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS logo_url TEXT;

-- Ajouter colonne pour notes/commentaires
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS notes TEXT;

-- Ajouter colonnes de traçabilité
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS last_modified_by UUID REFERENCES profiles(id);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS last_modified_at TIMESTAMP WITH TIME ZONE;

-- Fonction pour mettre à jour last_modified_at automatiquement
CREATE OR REPLACE FUNCTION update_supplier_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour last_modified_at
DROP TRIGGER IF EXISTS trigger_update_supplier_modified ON suppliers;
CREATE TRIGGER trigger_update_supplier_modified
    BEFORE UPDATE ON suppliers
    FOR EACH ROW
    EXECUTE FUNCTION update_supplier_modified();

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_suppliers_code ON suppliers(supplier_code);
CREATE INDEX IF NOT EXISTS idx_suppliers_active ON suppliers(active);

-- Commentaires pour documentation
COMMENT ON COLUMN suppliers.min_order_amount IS 'Montant minimum de commande en euros';
COMMENT ON COLUMN suppliers.ftp_path IS 'Chemin du dossier FTP pour ce fournisseur';
COMMENT ON COLUMN suppliers.transformation_id IS 'ID de la règle de transformation associée';
COMMENT ON COLUMN suppliers.logo_url IS 'URL ou chemin vers le logo du fournisseur';
COMMENT ON COLUMN suppliers.file_patterns IS 'Patterns de fichiers au format JSON array ex: ["Honda-*.csv"]';
COMMENT ON COLUMN suppliers.ftp_config IS 'Configuration FTP spécifique (host, port, credentials) si différent du global';
COMMENT ON COLUMN suppliers.transformation_rules IS 'Règles de transformation des fichiers au format JSON';
