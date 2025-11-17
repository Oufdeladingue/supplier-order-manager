-- Migration: Création de la table app_settings pour stocker les paramètres de l'application
-- Date: 2025-11-13
-- Description: Table unique pour stocker les paramètres globaux partagés entre tous les utilisateurs

-- Créer la table app_settings
CREATE TABLE IF NOT EXISTS app_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',  -- string, number, boolean, json
    description TEXT,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Commentaire sur la table
COMMENT ON TABLE app_settings IS 'Paramètres globaux de l''application partagés entre tous les utilisateurs';

-- Commentaires sur les colonnes
COMMENT ON COLUMN app_settings.setting_key IS 'Clé unique du paramètre (ex: ftp_host, ftp_port)';
COMMENT ON COLUMN app_settings.setting_value IS 'Valeur du paramètre (texte, peut contenir du JSON)';
COMMENT ON COLUMN app_settings.setting_type IS 'Type de la valeur: string, number, boolean, json';
COMMENT ON COLUMN app_settings.is_encrypted IS 'Indique si la valeur est chiffrée (ex: mot de passe)';

-- Insérer les paramètres FTP par défaut
INSERT INTO app_settings (setting_key, setting_value, setting_type, description, is_encrypted)
VALUES
    ('ftp_host', '', 'string', 'Hôte du serveur FTP/SFTP', FALSE),
    ('ftp_port', '22', 'number', 'Port du serveur FTP/SFTP', FALSE),
    ('ftp_username', '', 'string', 'Nom d''utilisateur FTP', FALSE),
    ('ftp_password', '', 'string', 'Mot de passe FTP', TRUE),
    ('ftp_remote_path', '/home/mjard_ep43/export-cdes-fournisseurs', 'string', 'Chemin distant sur le serveur FTP', FALSE),
    ('app_version', '1.0.0', 'string', 'Version de l''application', FALSE)
ON CONFLICT (setting_key) DO NOTHING;

-- Trigger pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_app_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER app_settings_updated_at_trigger
BEFORE UPDATE ON app_settings
FOR EACH ROW
EXECUTE FUNCTION update_app_settings_updated_at();

-- Afficher un message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Table app_settings créée avec succès';
END $$;
