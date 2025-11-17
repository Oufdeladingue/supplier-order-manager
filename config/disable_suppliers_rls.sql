-- Désactiver temporairement RLS sur la table suppliers pour les tests
-- ATTENTION : À utiliser uniquement en développement !

-- Désactiver RLS
ALTER TABLE suppliers DISABLE ROW LEVEL SECURITY;

-- Note : Pour réactiver RLS plus tard, utilisez :
-- ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
