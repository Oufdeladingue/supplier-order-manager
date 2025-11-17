-- Migration: Ajout de la colonne web_config à la table suppliers
-- Date: 2025-01-14
-- Description: Ajoute la colonne JSONB web_config pour stocker les paramètres de connexion web automatique

-- Ajouter la colonne web_config (JSONB) avec une valeur par défaut
ALTER TABLE suppliers
ADD COLUMN IF NOT EXISTS web_config JSONB DEFAULT '{
  "url": "",
  "client_code_enabled": false,
  "client_code_value": "",
  "client_code_selector": "",
  "login_value": "",
  "login_selector": "",
  "password_value": "",
  "password_selector": "",
  "other_enabled": false,
  "other_value": "",
  "other_selector": "",
  "submit_selector": "",
  "intermediate_enabled": false,
  "intermediate_selector": "",
  "cookie_enabled": false,
  "cookie_selector": "",
  "captcha_detect": false
}'::jsonb;

-- Vérification
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'suppliers'
AND column_name = 'web_config';
