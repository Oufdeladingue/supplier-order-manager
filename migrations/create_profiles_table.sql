-- Migration: Création de la table profiles pour les usernames
-- Date: 2025-01-17
-- Description: Permet aux utilisateurs de se connecter avec un username au lieu d'un email

-- Créer la table profiles
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Créer un index pour les recherches rapides par username
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);

-- Créer un index pour les recherches par email
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- Autoriser les lectures publiques (nécessaire pour le login)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre à tout le monde de lire les profils (nécessaire pour la recherche de username lors du login)
CREATE POLICY "Profiles are viewable by everyone" ON public.profiles
    FOR SELECT USING (true);

-- Politique pour permettre aux utilisateurs de mettre à jour leur propre profil
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Politique pour permettre aux utilisateurs de créer leur propre profil
CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour automatiquement updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Insérer le profil pour l'utilisateur existant
-- Remplacez 'votre_username' par le username souhaité
INSERT INTO public.profiles (id, username, email, display_name)
VALUES (
    '328cf874-2a86-4470-bfa0-65edcff9d9d9'::uuid,
    'mjardin',  -- Changez ce username selon vos préférences
    'contact@m-jardin.fr',
    'M. Jardin'  -- Nom d'affichage optionnel
)
ON CONFLICT (id) DO NOTHING;

-- Afficher un message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Table profiles créée avec succès !';
    RAISE NOTICE 'Vous pouvez maintenant vous connecter avec le username: mjardin';
END $$;
