# 📖 Guide d'installation détaillé

Ce guide vous accompagne pas à pas pour installer et configurer l'application sur vos deux postes Windows.

## ✅ Checklist avant installation

- [ ] Windows 10 ou 11 installé
- [ ] Droits administrateur sur le PC
- [ ] Connexion Internet active
- [ ] Compte Supabase Pro créé
- [ ] Accès aux identifiants email et FTP

## 🔧 Étape 1 : Installation de Python

### Télécharger Python

1. Allez sur [python.org/downloads](https://www.python.org/downloads/)
2. Téléchargez **Python 3.11** ou supérieur
3. Lancez l'installateur

### Installation

⚠️ **IMPORTANT** : Cochez **"Add Python to PATH"** avant de cliquer sur "Install Now"

![Python Installation](https://docs.python.org/3/_images/win_installer.png)

### Vérification

Ouvrez PowerShell et tapez :

```powershell
python --version
```

Vous devriez voir : `Python 3.11.x`

## 🔧 Étape 2 : Configuration de l'environnement

### Ouvrir PowerShell dans le dossier

1. Ouvrez l'Explorateur Windows
2. Naviguez vers `C:\Users\mjardin\Desktop\supplier-order-manager`
3. Dans la barre d'adresse, tapez `powershell` et appuyez sur Entrée

### Créer l'environnement virtuel

```powershell
python -m venv venv
```

Attendez quelques secondes...

### Activer l'environnement

```powershell
.\venv\Scripts\Activate.ps1
```

Si vous obtenez une erreur de politique d'exécution :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis réessayez d'activer.

Vous devriez voir `(venv)` apparaître avant votre prompt.

### Installer les dépendances

```powershell
pip install -r requirements.txt
```

⏱️ Cela prendra 2-5 minutes selon votre connexion.

## 🔧 Étape 3 : Configuration de Supabase

### A. Récupérer les clés d'API

1. Connectez-vous à [supabase.com](https://supabase.com)
2. Sélectionnez votre projet
3. Allez dans **Settings** → **API**
4. Copiez :
   - **Project URL** (ex: `https://abcdefgh.supabase.co`)
   - **anon public** (clé publique)
   - **service_role** (clé privée) ⚠️ À garder secrète !

### B. Créer la base de données

1. Dans Supabase, allez dans **SQL Editor**
2. Cliquez sur **New query**
3. Ouvrez le fichier `config/supabase_schema.sql` sur votre PC
4. Copiez tout le contenu
5. Collez dans l'éditeur SQL de Supabase
6. Cliquez sur **Run**

✅ Vous devriez voir : "Success. No rows returned"

### C. Créer les buckets de stockage

1. Allez dans **Storage**
2. Cliquez sur **New bucket**
3. Nom : `supplier-files-original`
   - Public : Non (recommandé)
   - Cliquez sur **Create bucket**
4. Répétez pour : `supplier-files-transformed`

### D. Créer les utilisateurs

1. Allez dans **Authentication** → **Users**
2. Cliquez sur **Add user**
3. Créez un compte pour chaque personne :
   - Email : `votre.nom@entreprise.com`
   - Mot de passe : Créez un mot de passe fort
   - Cochez "Auto Confirm User"
4. Répétez pour le 2ème utilisateur

## 🔧 Étape 4 : Configuration de l'application

### Créer le fichier .env

1. Ouvrez le fichier `.env.example` avec Notepad
2. Remplissez TOUTES les valeurs (voir ci-dessous)
3. Enregistrez sous le nom `.env` (sans .example)

### Exemple de .env complété

```env
# Supabase Configuration
SUPABASE_URL=https://abcdefgh.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Email Configuration (si vous utilisez Gmail)
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=commandes@votreentreprise.com
EMAIL_PASSWORD=abcd efgh ijkl mnop

# FTP/SFTP Configuration
FTP_HOST=ftp.fournisseur.com
FTP_PORT=22
FTP_USERNAME=votre_user
FTP_PASSWORD=votre_password
FTP_USE_SFTP=true

# Application Settings
APP_NAME=Gestionnaire Commandes Fournisseurs
APP_VERSION=1.0.0
LOG_LEVEL=INFO
COLLECTION_TIME=10:00
LOCAL_STORAGE_PATH=./data
TEMP_FOLDER=./temp
```

### Configuration Gmail

Si vous utilisez Gmail, créez un "App Password" :

1. Allez sur [myaccount.google.com](https://myaccount.google.com)
2. Sécurité → Validation en deux étapes (activez si nécessaire)
3. Sécurité → Mots de passe des applications
4. Sélectionnez "Autre" et nommez "Commandes Fournisseurs"
5. Copiez le mot de passe généré (16 caractères)
6. Utilisez-le dans `EMAIL_PASSWORD`

## 🔧 Étape 5 : Configuration des fournisseurs

### Éditer suppliers.json

1. Ouvrez `config/suppliers.json` avec Notepad
2. Remplacez les exemples par vos vrais fournisseurs

### Exemple pour 3 fournisseurs

```json
{
  "suppliers": [
    {
      "id": "FOURNISSEUR_A",
      "name": "Fournisseur Alpha",
      "email_pattern": "commandes@alpha.com",
      "file_patterns": ["*.csv"],
      "active": true,
      "source": "email",
      "transformation_id": "transform_alpha"
    },
    {
      "id": "FOURNISSEUR_B",
      "name": "Fournisseur Beta",
      "file_patterns": ["order_*.xlsx"],
      "active": true,
      "source": "ftp",
      "ftp_path": "/orders",
      "ftp_config": {
        "host": "ftp.beta.com",
        "port": 22,
        "username": "user_beta",
        "password": "pass_beta"
      },
      "transformation_id": "transform_beta"
    },
    {
      "id": "FOURNISSEUR_C",
      "name": "Fournisseur Gamma",
      "email_pattern": "orders@gamma.fr",
      "file_patterns": ["*.xlsx", "*.csv"],
      "active": true,
      "source": "email",
      "transformation_id": "transform_gamma"
    }
  ]
}
```

💡 Répétez le pattern pour vos 15 fournisseurs.

## 🔧 Étape 6 : Test de l'application

### Premier lancement

```powershell
python app/main.py
```

### Connexion

1. Une fenêtre de connexion apparaît
2. Entrez l'email et mot de passe d'un utilisateur Supabase
3. Cliquez sur "Se connecter"

✅ Si ça marche : Vous voyez l'interface principale !

❌ Si erreur : Vérifiez :
- Les clés Supabase dans `.env`
- Que l'utilisateur existe dans Authentication
- Les logs dans `logs/app_*.log`

## 🔧 Étape 7 : Configuration de la collecte automatique

### Modifier le script de planification

1. Ouvrez `worker/setup_scheduler.bat` avec Notepad
2. Modifiez les chemins :

```batch
set PYTHON_PATH=C:\Users\mjardin\Desktop\supplier-order-manager\venv\Scripts\python.exe
set SCRIPT_PATH=C:\Users\mjardin\Desktop\supplier-order-manager\worker\collector.py
set RUN_TIME=10:00
```

### Créer la tâche planifiée

1. Faites clic droit sur PowerShell → **Exécuter en tant qu'administrateur**
2. Naviguez vers le dossier :

```powershell
cd C:\Users\mjardin\Desktop\supplier-order-manager\worker
```

3. Exécutez :

```powershell
.\setup_scheduler.bat
```

✅ Vous devriez voir : "Tâche planifiée créée avec succès!"

### Vérifier la tâche

```powershell
schtasks /Query /TN "CollecteCommandesFournisseurs"
```

### Tester manuellement

```powershell
cd ..
python worker\collector.py
```

Regardez les logs dans `logs/collector_*.log`

## 🔧 Étape 8 : Installation sur le 2ème poste

Pour installer sur le deuxième PC :

1. Copiez tout le dossier `supplier-order-manager`
2. Répétez les étapes 2, 4 et 6
3. ⚠️ **NE PAS** refaire l'étape 3 (Supabase déjà configuré)
4. ⚠️ **NE PAS** reconfigurer la tâche planifiée (un seul worker suffit)

## ✅ Vérification finale

### Checklist

- [ ] L'application se lance sans erreur
- [ ] Vous pouvez vous connecter
- [ ] La liste des fichiers s'affiche (vide au début, c'est normal)
- [ ] La tâche planifiée est créée
- [ ] Les logs sont créés dans le dossier `logs/`

### Test de bout en bout

1. Lancez manuellement le collector :
   ```powershell
   python worker\collector.py
   ```

2. Vérifiez qu'il se connecte aux emails/FTP

3. Si des fichiers sont collectés, ils apparaissent dans l'application

4. Verrouillez un fichier dans l'interface

5. Sur le 2ème PC, lancez l'application et vérifiez que le verrou est visible

## 🆘 Problèmes courants

### "Python n'est pas reconnu..."

➡️ Python n'est pas dans le PATH. Réinstallez Python en cochant "Add to PATH"

### "Erreur de connexion Supabase"

➡️ Vérifiez les clés dans `.env` et que le schéma SQL a été exécuté

### "Cannot open connection to IMAP"

➡️ Vérifiez :
- Les identifiants email
- Que l'accès IMAP est activé
- Pour Gmail, utilisez un App Password

### "Permission denied" sur FTP

➡️ Testez avec FileZilla pour vérifier les identifiants

### La tâche planifiée ne s'exécute pas

➡️ Vérifiez :
- Que les chemins dans le .bat sont corrects
- Les logs dans `logs/collector_*.log`
- Le statut : `schtasks /Query /TN "CollecteCommandesFournisseurs"`

## 📞 Aide supplémentaire

Si vous êtes bloqué :

1. Consultez `README.md` pour plus de détails
2. Regardez les logs dans `logs/`
3. Vérifiez chaque étape de configuration

---

🎉 **Félicitations !** Votre application est installée et configurée !
