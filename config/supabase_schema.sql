-- Schéma SQL pour Supabase
-- À exécuter dans le SQL Editor de votre projet Supabase

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des profils utilisateurs (extend Supabase Auth)
CREATE TABLE IF NOT EXISTS profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des fournisseurs
CREATE TABLE IF NOT EXISTS suppliers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  supplier_code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email_pattern TEXT,
  file_patterns JSONB,
  source TEXT CHECK (source IN ('email', 'ftp', 'manual')),
  ftp_config JSONB,
  transformation_rules JSONB,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des fichiers reçus
CREATE TABLE IF NOT EXISTS files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  filename TEXT NOT NULL,
  supplier_id UUID REFERENCES suppliers(id),
  supplier_code TEXT NOT NULL,
  received_date DATE NOT NULL,
  file_type TEXT CHECK (file_type IN ('csv', 'xlsx', 'xls')),
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'error', 'merged')),

  -- Système de verrouillage collaboratif
  locked_by UUID REFERENCES profiles(id),
  locked_at TIMESTAMP WITH TIME ZONE,

  -- Traçabilité
  processed_by UUID REFERENCES profiles(id),
  processed_at TIMESTAMP WITH TIME ZONE,

  -- Chemins de stockage (Supabase Storage)
  original_path TEXT,
  transformed_path TEXT,

  -- Métadonnées
  row_count INTEGER,
  file_size INTEGER,
  error_message TEXT,

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table d'historique des traitements
CREATE TABLE IF NOT EXISTS processing_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_id UUID REFERENCES files(id) ON DELETE CASCADE,
  user_id UUID REFERENCES profiles(id),
  action TEXT NOT NULL CHECK (action IN ('uploaded', 'locked', 'unlocked', 'transformed', 'sent', 'merged', 'error')),
  details JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table pour les regroupements de fichiers
CREATE TABLE IF NOT EXISTS file_merges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  supplier_id UUID REFERENCES suppliers(id),
  merged_file_path TEXT NOT NULL,
  file_ids UUID[] NOT NULL,
  date_range_start DATE NOT NULL,
  date_range_end DATE NOT NULL,
  created_by UUID REFERENCES profiles(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);
CREATE INDEX IF NOT EXISTS idx_files_supplier ON files(supplier_code);
CREATE INDEX IF NOT EXISTS idx_files_received_date ON files(received_date);
CREATE INDEX IF NOT EXISTS idx_files_locked_by ON files(locked_by);
CREATE INDEX IF NOT EXISTS idx_processing_history_file_id ON processing_history(file_id);
CREATE INDEX IF NOT EXISTS idx_processing_history_created_at ON processing_history(created_at);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Fonction pour libérer automatiquement les verrous après 30 minutes d'inactivité
CREATE OR REPLACE FUNCTION unlock_stale_files()
RETURNS void AS $$
BEGIN
    UPDATE files
    SET locked_by = NULL, locked_at = NULL, status = 'pending'
    WHERE locked_at < NOW() - INTERVAL '30 minutes'
    AND status = 'processing';
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_merges ENABLE ROW LEVEL SECURITY;

-- Policies pour profiles
CREATE POLICY "Les utilisateurs peuvent voir tous les profils" ON profiles
    FOR SELECT USING (true);

CREATE POLICY "Les utilisateurs peuvent mettre à jour leur propre profil" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Policies pour suppliers
CREATE POLICY "Les utilisateurs authentifiés peuvent voir les fournisseurs" ON suppliers
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent créer des fournisseurs" ON suppliers
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent mettre à jour les fournisseurs" ON suppliers
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Policies pour files
CREATE POLICY "Les utilisateurs authentifiés peuvent voir tous les fichiers" ON files
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent créer des fichiers" ON files
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent mettre à jour les fichiers" ON files
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Policies pour processing_history
CREATE POLICY "Les utilisateurs authentifiés peuvent voir l'historique" ON processing_history
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent créer des entrées d'historique" ON processing_history
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Policies pour file_merges
CREATE POLICY "Les utilisateurs authentifiés peuvent voir les regroupements" ON file_merges
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Les utilisateurs authentifiés peuvent créer des regroupements" ON file_merges
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Storage Buckets (à créer via l'interface Supabase Storage ou via l'API)
-- Bucket: 'supplier-files-original' (fichiers reçus)
-- Bucket: 'supplier-files-transformed' (fichiers transformés)

-- Insertion de données de test (optionnel)
-- INSERT INTO suppliers (supplier_code, name, source, active) VALUES
-- ('SUP001', 'Fournisseur Test 1', 'email', true),
-- ('SUP002', 'Fournisseur Test 2', 'ftp', true);
