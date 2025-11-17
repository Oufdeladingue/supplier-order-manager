-- Table pour stocker les paramètres de l'organisation (FTP, etc.)
-- Ces paramètres sont partagés par tous les utilisateurs

CREATE TABLE IF NOT EXISTS organization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_name TEXT NOT NULL DEFAULT 'default',

    -- Identifiants FTP
    ftp_host TEXT,
    ftp_port INTEGER DEFAULT 22,
    ftp_username TEXT,
    ftp_password TEXT, -- Stocké en clair car c'est en interne, mais pourrait être chiffré
    ftp_path TEXT,

    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id),

    -- Contrainte : une seule organisation pour l'instant
    CONSTRAINT unique_organization UNIQUE (organization_name)
);

-- Index
CREATE INDEX IF NOT EXISTS idx_organization_settings_name ON organization_settings(organization_name);

-- RLS (Row Level Security) - Tous les utilisateurs authentifiés peuvent lire
ALTER TABLE organization_settings ENABLE ROW LEVEL SECURITY;

-- Policy de lecture : tous les utilisateurs authentifiés peuvent lire
CREATE POLICY "Lecture des paramètres organisation"
    ON organization_settings
    FOR SELECT
    TO authenticated
    USING (true);

-- Policy d'écriture : réservé aux admins (à définir selon vos besoins)
-- Pour l'instant, on permet à tous les utilisateurs authentifiés
CREATE POLICY "Modification des paramètres organisation"
    ON organization_settings
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_organization_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER organization_settings_updated_at
    BEFORE UPDATE ON organization_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_organization_settings_updated_at();

-- Insérer les paramètres par défaut avec vos identifiants FTP
INSERT INTO organization_settings (
    organization_name,
    ftp_host,
    ftp_port,
    ftp_username,
    ftp_password,
    ftp_path
) VALUES (
    'default',
    '217.182.241.73',
    22,
    'mjard_ep43',
    'pmqDKR98CnbRPwbgemfA2',
    '/home/mjard_ep43/export-cdes-fournisseurs'
)
ON CONFLICT (organization_name) DO UPDATE SET
    ftp_host = EXCLUDED.ftp_host,
    ftp_port = EXCLUDED.ftp_port,
    ftp_username = EXCLUDED.ftp_username,
    ftp_password = EXCLUDED.ftp_password,
    ftp_path = EXCLUDED.ftp_path;

-- Commentaires
COMMENT ON TABLE organization_settings IS 'Paramètres partagés de l''organisation (FTP, etc.)';
COMMENT ON COLUMN organization_settings.ftp_password IS 'Mot de passe FTP - Stocké en clair pour usage interne';
