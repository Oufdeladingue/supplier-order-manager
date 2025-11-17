# 📦 Gestionnaire de Commandes Fournisseurs

Application de bureau pour gérer et automatiser les commandes fournisseurs.

## ✨ Fonctionnalités

### 📋 Gestion des Fichiers
- **Importation automatique** : Récupération des fichiers depuis un dossier configuré
- **Filtrage par fournisseur** : Organisation des fichiers par fournisseur
- **Prévisualisation** : Affichage du contenu des fichiers avant traitement
- **Export personnalisé** : Génération de fichiers CSV/XLSX avec mise en forme automatique
- **Tri automatique** : Tri alphabétique des références
- **Ajustement des colonnes** : Largeurs auto-ajustées dans les exports Excel

### 🏢 Gestion des Fournisseurs
- **Configuration complète** : Paramètres d'import/export par fournisseur
- **Colonnes personnalisées** : Suppression, fusion et renommage de colonnes
- **En-têtes dynamiques** : Support des placeholders `{date}` et `{supplier}`
- **Préfixes intelligents** : Suppression automatique des préfixes de références
- **Gestion des doublons** : Regroupement et totalisation intelligente

### 🌐 Automatisation Web
- **Ouverture automatique** : Lancement des sites fournisseurs avec les bons filtres
- **Navigation intelligente** : Gestion des popups et cookies
- **Connexion automatique** : Remplissage des formulaires de login (optionnel)
- **Multi-navigateur** : Support de Chrome, Firefox, Edge, Opera, Brave

### ⚙️ Paramètres
- **Par utilisateur** : Stockés dans Supabase (synchronisés entre postes)
- **Par poste** : Dossier de sortie, navigateur, intervalle de rafraîchissement
- **Authentification** : Login par email ou nom d'utilisateur
- **Rafraîchissement auto** : Actualisation périodique de la liste (0-3600 secondes)

### 🔄 Mises à jour automatiques
- **Vérification au démarrage** : Détection des nouvelles versions sur GitHub
- **Installation facile** : Téléchargement et remplacement automatique
- **Notifications** : Alertes pour les mises à jour disponibles

## 📋 Prérequis

### Pour l'exécutable
- Windows 10/11
- Connexion Internet (pour Supabase et les mises à jour)

### Pour le code source
- Python 3.10+
- Compte Supabase (gratuit)
- Variables d'environnement :
  - `SUPABASE_URL` : URL de votre projet Supabase
  - `SUPABASE_KEY` : Clé anon de votre projet Supabase

## 🚀 Installation

### Méthode 1 : Télécharger l'exécutable (recommandé)
1. Allez dans [Releases](https://github.com/Oufdeladingue/supplier-order-manager/releases)
2. Téléchargez la dernière version `SupplierOrderManager.exe`
3. Lancez l'exécutable

### Méthode 2 : Depuis le code source
```bash
# Cloner le dépôt
git clone https://github.com/Oufdeladingue/supplier-order-manager.git
cd supplier-order-manager

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app/main.py
```

## 🔧 Configuration

### 1. Base de données Supabase
Exécutez les migrations SQL dans l'ordre :
```sql
-- 1. Créer la table profiles
migrations/create_profiles_table_v2.sql

-- 2. Créer la table suppliers et autres tables nécessaires
-- (exécutez les autres migrations selon vos besoins)
```

### 2. Premier utilisateur
Créez votre premier utilisateur dans Supabase :
1. Allez dans **Authentication** > **Users**
2. Créez un utilisateur avec email et mot de passe
3. Ajoutez son profil dans la table `profiles` avec un username

### 3. Configuration du poste
Au premier lancement :
1. Connectez-vous avec votre email ou username
2. Allez dans **Paramètres** > **Paramètres du poste**
3. Configurez :
   - Dossier de sortie pour les exports
   - Navigateur préféré
   - Intervalle de rafraîchissement (optionnel)

## 📦 Compilation

Pour créer un exécutable :
```bash
python build_exe.py
```

L'exécutable sera généré dans `dist/SupplierOrderManager.exe`

## 🔄 Workflow de mise à jour

1. Modifier le code source
2. Incrémenter la version dans `app/main.py` (variable `__version__`)
3. Compiler l'application : `python build_exe.py`
4. Créer une release sur GitHub avec l'exécutable
5. Les utilisateurs seront notifiés au prochain lancement

## 🛠️ Technologies utilisées

- **Interface** : PySide6 (Qt)
- **Base de données** : Supabase (PostgreSQL)
- **Automation Web** : Selenium + WebDriver Manager
- **Export** : Pandas + openpyxl
- **Logs** : Loguru
- **Compilation** : PyInstaller

## 📞 Support

Pour toute question ou problème, contactez l'administrateur système.

## 📝 Licence

Propriétaire - Usage interne uniquement

## 👥 Auteurs

- M. Jardin - Développement initial

---

**Version actuelle** : v1.0.0
**Dernière mise à jour** : 17 janvier 2025
