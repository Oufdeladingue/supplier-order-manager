# Système de Gestion des Fournisseurs - Guide de démarrage

## 📦 Fichiers créés

### Scripts SQL

1. **`config/update_suppliers_extended_schema.sql`**
   - Mise à jour du schéma de la table `suppliers`
   - Ajout des colonnes : phone, email, website, web_user, web_password, file_filter_slug, import_config
   - À exécuter dans Supabase SQL Editor

### Scripts Python

2. **`extract_suppliers_from_ftp.py`**
   - Analyse automatique des fichiers FTP
   - Extraction des noms de fournisseurs
   - Création automatique dans la base de données
   - À exécuter une seule fois pour l'initialisation

### Interface utilisateur

3. **`app/ui/suppliers_manager_dialog_v2.py`**
   - Nouvelle interface de gestion des fournisseurs
   - Système d'onglets (Informations générales + Import)
   - Formulaire complet avec tous les champs
   - Remplace l'ancienne version

4. **`app/ui/main_window.py`** (modifié)
   - Mise à jour de l'import pour utiliser `suppliers_manager_dialog_v2`
   - Ligne 590 : `from app.ui.suppliers_manager_dialog_v2 import SuppliersManagerDialog`

### Documentation

5. **`GESTION_FOURNISSEURS.md`**
   - Guide complet d'utilisation
   - Exemples et cas d'usage
   - Dépannage

6. **`README_FOURNISSEURS.md`** (ce fichier)
   - Vue d'ensemble
   - Guide de démarrage rapide

## 🚀 Mise en place (5 minutes)

### Étape 1 : Mise à jour de la base de données

```bash
# 1. Ouvrez Supabase Dashboard
# 2. Allez dans SQL Editor
# 3. Copiez le contenu de config/update_suppliers_extended_schema.sql
# 4. Cliquez sur "Run"
```

**Vérification** : Dans Table Editor > suppliers, vous devriez voir les nouvelles colonnes :
- phone
- email
- website
- web_user
- web_password
- file_filter_slug
- import_config

### Étape 2 : Extraction automatique des fournisseurs

```bash
python extract_suppliers_from_ftp.py
```

**Résultat attendu** :
```
✅ Créés:  18
⏭️  Ignorés: 0
❌ Erreurs: 0
```

### Étape 3 : Lancement de l'application

```bash
python app/main.py
```

### Étape 4 : Compléter les informations

1. Dans l'application, cliquez sur **"📦 Gérer Fournisseurs"**
2. Double-cliquez sur chaque fournisseur
3. Complétez les informations manquantes :
   - **Onglet "Informations générales"** :
     - Logo, Téléphone, Email, Site web
     - Identifiant et mot de passe web
   - **Onglet "Import"** :
     - Format de sortie (xlsx/csv)
     - Présence d'en-tête
     - Conservation des zéros significatifs

## 📋 Checklist de vérification

- [ ] Script SQL exécuté dans Supabase
- [ ] Nouvelles colonnes visibles dans la table suppliers
- [ ] Script d'extraction exécuté avec succès
- [ ] 18 fournisseurs créés dans la base
- [ ] Application lance sans erreur
- [ ] Fenêtre "Gestion des Fournisseurs" s'ouvre correctement
- [ ] Tous les fournisseurs apparaissent dans le tableau
- [ ] Double-clic ouvre le formulaire d'édition
- [ ] Les deux onglets sont visibles (Informations générales + Import)
- [ ] Sauvegarde fonctionne sans erreur

## 🎯 Informations à compléter par fournisseur

### Priorité 1 (Essentiel)

- ✅ Nom (déjà rempli automatiquement)
- ✅ Slug de filtre (déjà rempli = nom du fournisseur)
- ✅ Patterns de fichiers (déjà rempli)
- ⚙️ Format de sortie (xlsx par défaut)
- ⚙️ En-tête (non par défaut)

### Priorité 2 (Important)

- 📞 Téléphone
- 📧 Email
- 🌐 Site web
- 🔑 Identifiant web
- 🔑 Mot de passe web

### Priorité 3 (Optionnel)

- 🖼️ URL Logo
- ⚙️ Zéros significatifs

## 📊 Structure des données

### Table `suppliers`

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `name` | TEXT | Nom du fournisseur | `Honda` |
| `file_filter_slug` | TEXT | Slug pour filtrer les fichiers | `Honda` |
| `logo_url` | TEXT | URL du logo | `https://...` |
| `phone` | TEXT | Téléphone | `01 23 45 67 89` |
| `email` | TEXT | Email | `contact@honda.fr` |
| `website` | TEXT | Site web | `https://www.honda.fr` |
| `web_user` | TEXT | Identifiant espace client | `mon_compte` |
| `web_password` | TEXT | Mot de passe espace client | `password123` |
| `import_config` | JSONB | Configuration d'import | `{"output_format":"xlsx",...}` |

### JSON `import_config`

```json
{
  "output_format": "xlsx",      // ou "csv"
  "has_header": false,           // true si en-tête présent
  "leading_zeros": false         // true pour conserver 00123
}
```

## 🔧 Utilisation quotidienne

### Ajouter un nouveau fournisseur

1. Ouvrir "Gestion des Fournisseurs"
2. Cliquer "➕ Nouveau Fournisseur"
3. Remplir les deux onglets
4. Sauvegarder

### Modifier un fournisseur existant

1. Double-cliquer sur la ligne du fournisseur
2. Modifier les informations
3. Sauvegarder

### Désactiver un fournisseur temporairement

1. Éditer le fournisseur
2. Décocher "Fournisseur actif"
3. Sauvegarder

## 🎓 Exemples de configuration

### Exemple 1 : Honda (simple)

**Onglet Informations générales :**
- Nom : `Honda`
- Slug : `Honda`
- Téléphone : `01 23 45 67 89`
- Email : `commandes@honda.fr`
- Site web : `https://www.honda.fr`
- Patterns : `Honda-*.csv`

**Onglet Import :**
- Format : `xlsx`
- En-tête : `Non coché` (pas d'en-tête)
- Zéros : `Non coché`

### Exemple 2 : M-Jardin (patterns multiples)

**Onglet Informations générales :**
- Nom : `M-Jardin`
- Slug : `M-Jardin` ou `M Jardin` (selon les fichiers)
- Patterns :
  ```
  M-Jardin-*.csv
  M-Jardin Bleu-*.csv
  M Jardin-*.csv
  M Jardin Bleu-*.csv
  ```

**Onglet Import :**
- Format : `xlsx`
- En-tête : `Coché` (fichier avec en-tête)
- Zéros : `Coché` (codes produits avec zéros)

### Exemple 3 : Iseki France (cas complexe)

**Onglet Informations générales :**
- Nom : `Iseki France`
- Slug : `Iseki France`
- Patterns :
  ```
  Iseki France-*.csv
  Iseki France (accessoires)-*.csv
  ```

**Onglet Import :**
- Format : `csv`
- En-tête : `Non coché`
- Zéros : `Non coché`

## 🔄 Synchronisation temps réel

Toutes les modifications sont automatiquement synchronisées entre tous les utilisateurs connectés :

- ✅ Ajout d'un fournisseur → Visible immédiatement
- ✅ Modification → Mise à jour instantanée
- ✅ Suppression → Retirée partout
- ✅ Pas besoin de rafraîchir manuellement

## 📞 Support

En cas de problème :

1. Consultez `GESTION_FOURNISSEURS.md` (section Dépannage)
2. Vérifiez les logs dans `logs/`
3. Testez la connexion Supabase : `python test_connection.py`
4. Vérifiez le schéma de la table dans Supabase Table Editor

## 🎉 Prochaines fonctionnalités

Une fois les fournisseurs configurés, vous pourrez :

- [ ] Filtrer les fichiers FTP par fournisseur dans la fenêtre principale
- [ ] Appliquer automatiquement les règles d'import
- [ ] Générer des rapports par fournisseur
- [ ] Exporter les coordonnées fournisseurs
- [ ] Suivre l'historique des commandes par fournisseur

## 📝 Notes importantes

- **Slug de filtre** : Doit correspondre EXACTEMENT aux premières lettres du nom de fichier
- **Mot de passe** : Stocké en clair pour le moment (à chiffrer si sensible)
- **Suppression** : Préférer la désactivation pour conserver l'historique
- **Patterns** : Un par ligne, supporte les wildcards (`*`)

---

**Version** : 2.0
**Dernière mise à jour** : 13 novembre 2025
