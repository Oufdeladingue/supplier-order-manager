# Gestion des Fournisseurs

## 🎯 Vue d'ensemble

La nouvelle interface de gestion des fournisseurs permet de centraliser toutes les informations relatives à vos fournisseurs dans la base de données Supabase. Les données sont synchronisées en temps réel entre tous les utilisateurs.

## 📋 Mise en place initiale

### 1. Mise à jour du schéma de la base de données

Exécutez le script SQL dans Supabase Dashboard :

```sql
-- Fichier: config/update_suppliers_extended_schema.sql
```

Dans Supabase :
1. Allez dans **SQL Editor**
2. Copiez le contenu de `config/update_suppliers_extended_schema.sql`
3. Cliquez sur **Run**

### 2. Extraction automatique des fournisseurs depuis FTP

Pour créer automatiquement les fournisseurs à partir des fichiers présents sur le FTP :

```bash
python extract_suppliers_from_ftp.py
```

Ce script :
- Se connecte au serveur FTP
- Analyse tous les noms de fichiers
- Extrait les noms de fournisseurs uniques
- Les crée dans la base de données avec une configuration par défaut

**Exemple de sortie :**
```
==========================================
EXTRACTION DES FOURNISSEURS DEPUIS FTP
==========================================

[OK] Connexion Supabase établie
[INFO] Connexion au serveur FTP 217.182.241.73...
[OK] 28 fichier(s) trouvé(s)

[INFO] 18 fournisseur(s) unique(s) détecté(s):

  • Honda
    - 1 fichier(s)
    - Exemples: Honda-13-11-25.csv

  • Husqvarna
    - 2 fichier(s)
    - Exemples: Husqvarna-11-11-25.csv, Husqvarna-13-11-25.csv

...

✅ Créés:  18
⏭️  Ignorés: 0
❌ Erreurs: 0
```

## 🎮 Utilisation de l'interface

### Accès

Dans l'application, cliquez sur **"📦 Gérer Fournisseurs"** dans la barre d'outils.

### Vue d'ensemble

La fenêtre affiche un tableau avec tous les fournisseurs et leurs informations principales :
- **Nom** : Nom du fournisseur
- **Slug filtre** : Premières lettres pour filtrer les fichiers
- **Téléphone** : Numéro de téléphone
- **Email** : Adresse email
- **Site web** : URL du site web
- **Patterns** : Patterns de fichiers (ex: Honda-*.csv)
- **Format sortie** : Format du fichier transformé (XLSX ou CSV)
- **Actif** : ✓ si actif, ✗ si inactif
- **Modifié** : Date de dernière modification

### Ajouter un fournisseur

1. Cliquez sur **"➕ Nouveau Fournisseur"**
2. Remplissez les informations dans les deux onglets
3. Cliquez sur **"💾 Sauvegarder"**

### Modifier un fournisseur

- **Double-cliquez** sur une ligne du tableau
- **OU** sélectionnez une ligne et cliquez sur **"✏️ Modifier"**

### Supprimer un fournisseur

1. Sélectionnez un fournisseur dans le tableau
2. Cliquez sur **"🗑️ Supprimer"**
3. Confirmez la suppression

## 📝 Formulaire d'édition

Le formulaire est divisé en **2 onglets** :

### Onglet 1 : Informations générales

#### **Informations de base**

- **Nom*** : Nom d'affichage du fournisseur (ex: `Honda`)
- **Slug de filtre*** : Premières lettres du nom de fichier pour filtrer
  - Exemple : `Honda` pour filtrer `Honda-13-11-25.csv`
  - Exemple : `M-Jardin` pour filtrer `M-Jardin-13-11-25.csv` et `M-Jardin Bleu-13-11-25.csv`
- **URL Logo** : Lien vers le logo du fournisseur (optionnel)
- **Status** : Cocher si le fournisseur est actif

#### **Coordonnées**

- **Téléphone** : Numéro de téléphone du fournisseur
- **Email** : Adresse email du fournisseur
- **Site web** : URL du site web (ex: `https://www.honda.fr`)

#### **Accès espace client web**

- **Identifiant** : Nom d'utilisateur pour l'espace client
- **Mot de passe** : Mot de passe pour l'espace client
- Cocher **"Afficher le mot de passe"** pour voir le mot de passe en clair

#### **Configuration FTP**

- **Source** : `ftp`, `email` ou `manual`
- **Chemin FTP** : Chemin sur le serveur SFTP (ex: `/home/mjard_ep43/export-cdes-fournisseurs`)
- **Patterns fichiers*** : Un pattern par ligne
  ```
  Honda-*.csv
  Honda_*.xlsx
  ```

### Onglet 2 : Import

Configuration des paramètres d'import et de transformation des fichiers.

#### **Format de sortie**

- **xlsx** : Fichier Excel (recommandé)
- **csv** : Fichier CSV

#### **En-tête**

- Cocher si le fichier source contient une ligne d'en-tête avec les noms de colonnes
- Laisser décoché si la première ligne contient déjà des données

**Exemple :**

Fichier **AVEC en-tête** :
```
Référence;Désignation;Quantité;Prix
REF001;Produit A;5;100.00
REF002;Produit B;3;50.00
```

Fichier **SANS en-tête** (cas par défaut) :
```
REF001;Produit A;5;100.00
REF002;Produit B;3;50.00
```

#### **Zéros significatifs**

- Cocher pour conserver les zéros en début de valeur
- Utile pour les codes produits comme `00123`, `00456`, etc.

**Exemple :**

Sans conservation (décoché) : `00123` devient `123`
Avec conservation (coché) : `00123` reste `00123`

#### **Exemple de configuration**

Un panneau en temps réel affiche la configuration actuelle et son effet.

## 🔍 Slug de filtre - Cas d'usage

Le **slug de filtre** permet de filtrer les fichiers FTP pour chaque fournisseur.

### Exemples

| Fournisseur | Slug de filtre | Fichiers correspondants |
|-------------|----------------|------------------------|
| Honda | `Honda` | `Honda-13-11-25.csv` |
| Husqvarna | `Husqvarna` | `Husqvarna-11-11-25.csv`, `Husqvarna-13-11-25.csv` |
| M-Jardin | `M-Jardin` | `M-Jardin-13-11-25.csv`, `M-Jardin Bleu-13-11-25.csv` |
| M-Jardin | `M Jardin` | `M Jardin-13-11-25.csv`, `M Jardin Bleu-13-11-25.csv` |
| Iseki France | `Iseki France` | `Iseki France-13-11-25.csv`, `Iseki France (accessoires)-13-11-25.csv` |

**Important** : Le slug doit correspondre exactement aux premières lettres du nom de fichier (avant le premier `-`).

## 🔄 Synchronisation

Toutes les modifications sont **immédiatement synchronisées** entre tous les utilisateurs :

- Utilisateur A ajoute un fournisseur → Visible instantanément pour tous
- Utilisateur B modifie un téléphone → Mis à jour pour tous
- Pas besoin de redémarrer l'application

## 🗄️ Structure de données

Les informations sont stockées dans la table `suppliers` de Supabase :

```sql
suppliers (
  id UUID,
  supplier_code TEXT,           -- Code unique généré automatiquement
  name TEXT,                     -- Nom d'affichage
  file_filter_slug TEXT,         -- Slug de filtre pour les fichiers
  logo_url TEXT,                 -- URL du logo

  -- Coordonnées
  phone TEXT,
  email TEXT,
  website TEXT,

  -- Accès web
  web_user TEXT,
  web_password TEXT,

  -- Configuration FTP
  source TEXT,                   -- 'ftp', 'email', 'manual'
  ftp_path TEXT,
  file_patterns JSONB,           -- Array de patterns

  -- Configuration import
  import_config JSONB,           -- {output_format, has_header, leading_zeros}

  -- Métadonnées
  active BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  last_modified_by UUID,
  last_modified_at TIMESTAMP
)
```

### Exemple de `import_config` :

```json
{
  "output_format": "xlsx",
  "has_header": false,
  "leading_zeros": false
}
```

## 🔐 Sécurité

- ✅ Tous les utilisateurs authentifiés peuvent voir et modifier les fournisseurs
- ❌ Les utilisateurs non authentifiés n'ont aucun accès
- 🔒 Les mots de passe web sont stockés en texte clair (prévoir chiffrement si nécessaire)

## 🆘 Dépannage

### Erreur "Column does not exist: phone"

→ Exécutez le script SQL `update_suppliers_extended_schema.sql` dans Supabase

### Les modifications ne s'affichent pas

→ Cliquez sur le bouton **"🔄 Rafraîchir"** dans la liste des fournisseurs

### Impossible de créer un fournisseur

→ Vérifiez que :
- Le nom est renseigné
- Le slug de filtre est renseigné
- Au moins un pattern de fichier est défini

### Double-clic ne fonctionne pas

→ Sélectionnez d'abord la ligne, puis cliquez sur **"✏️ Modifier"**

## 📞 Prochaines étapes

Une fois les fournisseurs configurés, vous pourrez :

1. **Filtrer les fichiers FTP par fournisseur** dans la fenêtre principale
2. **Appliquer automatiquement les règles d'import** lors de la transformation
3. **Générer des rapports par fournisseur** avec les coordonnées
4. **Suivre l'historique des commandes** par fournisseur

## 💡 Bonnes pratiques

1. **Complétez toutes les informations** même si optionnelles (téléphone, email, site web)
2. **Testez le slug de filtre** en regardant les fichiers qui apparaissent dans la liste
3. **Vérifiez les paramètres d'import** en ouvrant un fichier exemple
4. **Conservez les identifiants web** à jour pour faciliter l'accès aux espaces clients
5. **Désactivez les fournisseurs obsolètes** plutôt que de les supprimer (pour l'historique)
