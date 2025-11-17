# Migration des Fournisseurs vers la Base de Données

## 🎯 Objectif

Passer du stockage des fournisseurs en fichier JSON local vers la base de données Supabase pour une synchronisation en temps réel entre tous les utilisateurs.

## ✅ Avantages

- **Synchronisation instantanée** entre tous les postes
- **Modifications partagées** : Un changement est visible par tous
- **Historique des modifications**
- **Interface de gestion** complète dans l'application
- **Pas de conflit de fichiers**

## 📋 Étapes de Migration

### 1. Mise à jour du schéma Supabase

Exécutez le script SQL dans votre projet Supabase :

```sql
-- Fichier: config/update_suppliers_schema.sql
```

Dans Supabase Dashboard :
1. Allez dans **SQL Editor**
2. Copiez le contenu de `config/update_suppliers_schema.sql`
3. Cliquez sur **Run**

### 2. Migration des données

Exécutez le script de migration :

```bash
python migrate_suppliers_to_db.py
```

Ce script :
- Lit le fichier `config/suppliers.json`
- Importe tous les fournisseurs dans Supabase
- Vérifie les doublons
- Affiche un résumé

### 3. Vérification

Dans Supabase Dashboard :
1. Allez dans **Table Editor**
2. Ouvrez la table `suppliers`
3. Vérifiez que vos 18 fournisseurs sont bien importés

## 🎮 Utilisation dans l'Application

### Accès à la Gestion des Fournisseurs

Dans l'application, cliquez sur **"📦 Gérer Fournisseurs"** dans la barre d'outils.

### Fonctionnalités

#### **Liste des Fournisseurs**
- Tableau avec tous les fournisseurs
- Tri automatique par nom
- Affichage du statut (actif/inactif)

#### **Ajouter un Fournisseur**
1. Cliquez sur **"➕ Nouveau Fournisseur"**
2. Remplissez le formulaire :
   - **Code*** : Identifiant unique (ex: `honda`)
   - **Nom*** : Nom d'affichage (ex: `Honda`)
   - **Source*** : `ftp`, `email` ou `manual`
   - **Chemin FTP** : Chemin sur le serveur SFTP
   - **Patterns fichiers*** : Un pattern par ligne
     ```
     Honda-*.csv
     Honda_*.xlsx
     ```
   - **Email** : Pattern email (optionnel)
   - **ID Transformation** : ex: `transform_honda`
   - **Minimum commande** : Montant en euros
   - **URL Logo** : Lien vers le logo (optionnel)
   - **Actif** : Cocher si le fournisseur est actif
   - **Notes** : Commentaires libres
3. Cliquez sur **"💾 Sauvegarder"**

#### **Modifier un Fournisseur**
- Double-cliquez sur une ligne
- OU sélectionnez et cliquez **"✏️ Modifier"**
- Modifiez les champs
- Sauvegardez

#### **Supprimer un Fournisseur**
1. Sélectionnez un fournisseur
2. Cliquez sur **"🗑️ Supprimer"**
3. Confirmez

## 🔄 Synchronisation

Les modifications sont **instantanément synchronisées** :

- **Utilisateur A** ajoute un fournisseur → **Utilisateur B** le voit immédiatement
- **Utilisateur B** modifie un seuil → **Utilisateur A** voit le nouveau montant
- Pas besoin de redémarrer l'application

## 📝 Structure de la Table

```sql
suppliers (
  id UUID PRIMARY KEY,
  supplier_code TEXT UNIQUE NOT NULL,  -- Code unique
  name TEXT NOT NULL,                   -- Nom d'affichage
  email_pattern TEXT,                   -- Pattern email
  file_patterns JSONB,                  -- Array de patterns
  source TEXT,                          -- 'email', 'ftp', 'manual'
  ftp_config JSONB,                     -- Config FTP spécifique
  ftp_path TEXT,                        -- Chemin FTP
  transformation_id TEXT,               -- ID transformation
  transformation_rules JSONB,           -- Règles de transformation
  min_order_amount DECIMAL(10,2),       -- Montant minimum
  logo_url TEXT,                        -- URL du logo
  active BOOLEAN,                       -- Actif/Inactif
  notes TEXT,                           -- Commentaires
  last_modified_by UUID,                -- Qui a modifié
  last_modified_at TIMESTAMP,           -- Quand modifié
  created_at TIMESTAMP,                 -- Date création
  updated_at TIMESTAMP                  -- Date MAJ auto
)
```

## 🔐 Sécurité

Les policies RLS (Row Level Security) de Supabase garantissent que :
- ✅ Tous les utilisateurs authentifiés peuvent **voir** les fournisseurs
- ✅ Tous les utilisateurs authentifiés peuvent **créer/modifier** les fournisseurs
- ❌ Les utilisateurs non authentifiés **n'ont aucun accès**

## 🗑️ Fichier JSON

Après la migration, le fichier `config/suppliers.json` peut être :
- **Conservé** comme backup
- **Archivé** dans un dossier `old/`
- **Supprimé** si vous n'en avez plus besoin

L'application utilise désormais **exclusivement la base de données**.

## 🆘 Dépannage

### Erreur "Table suppliers not found"
→ Exécutez le script SQL `update_suppliers_schema.sql` dans Supabase

### Erreur "Column does not exist"
→ Vérifiez que toutes les colonnes ont été créées avec le script SQL

### Doublons lors de la migration
→ Normal si vous relancez le script. Les doublons sont ignorés

### Modifications non visibles par les autres utilisateurs
→ Vérifiez que tous utilisent la même base Supabase
→ Rafraîchissez la liste avec le bouton "🔄 Rafraîchir"

## 📞 Support

En cas de problème :
1. Consultez les logs dans `logs/`
2. Vérifiez la connexion Supabase
3. Testez avec `python test_connection.py`
