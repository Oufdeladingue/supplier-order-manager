-- Configurer les permissions pour le bucket supplier-logos
-- À exécuter dans Supabase SQL Editor

-- Policy pour permettre la lecture publique des logos
CREATE POLICY "Public Access for supplier logos"
ON storage.objects FOR SELECT
USING (bucket_id = 'supplier-logos');

-- Policy pour permettre l'insertion (upload) aux utilisateurs authentifiés
CREATE POLICY "Authenticated users can upload supplier logos"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'supplier-logos');

-- Policy pour permettre la mise à jour aux utilisateurs authentifiés
CREATE POLICY "Authenticated users can update supplier logos"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'supplier-logos');

-- Policy pour permettre la suppression aux utilisateurs authentifiés
CREATE POLICY "Authenticated users can delete supplier logos"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'supplier-logos');
