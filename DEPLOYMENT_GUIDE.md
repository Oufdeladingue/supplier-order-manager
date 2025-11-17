# Guide de déploiement - Gestionnaire Commandes Fournisseurs v1.0.3

## 📋 Résumé des améliorations

### ✅ Problèmes corrigés

1. **Versioning unifié**
   - Une seule source de vérité : `app/version.py`
   - Version correctement affichée dans "À propos"
   - Vérification de mise à jour cohérente

2. **Installeur professionnel Inno Setup**
   - Installation dans Program Files
   - Détection et désinstallation automatique des anciennes versions
   - Raccourcis menu Démarrer + bureau (optionnel)
   - Désinstalleur propre

3. **Système de mise à jour automatique**
   - Téléchargement automatique depuis GitHub
   - Barre de progression
   - Installation silencieuse
   - Redémarrage automatique
   - **Plus besoin d'aller sur GitHub manuellement !**

## 🚀 Processus de déploiement

### Étape 1 : Préparer une nouvelle version

1. **Mettre à jour la version**
   ```python
   # app/version.py
   __version__ = "1.0.4"  # Incrémenter
   ```

2. **Compiler l'exécutable**
   ```bash
   python build_exe.py
   ```

3. **Créer l'installeur**
   - Mettre à jour la version dans `installer.iss` (ligne 5)
   - Compiler avec Inno Setup :
     ```bash
     "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
     ```

### Étape 2 : Publier sur GitHub

1. **Commit et push**
   ```bash
   git add .
   git commit -m "feat: nouvelle fonctionnalité XYZ - v1.0.4"
   git push
   ```

2. **Créer une release**
   - Aller sur https://github.com/Oufdeladingue/supplier-order-manager/releases/new
   - Tag : `v1.0.4`
   - Titre : `v1.0.4 - Description courte`
   - Uploader : `installer_output/SupplierOrderManager-Setup-v1.0.4.exe`
   - Publier

### Étape 3 : Les utilisateurs reçoivent la mise à jour

**Automatiquement !**
1. Au démarrage, l'application vérifie les mises à jour
2. Si une mise à jour est disponible, l'utilisateur reçoit une notification
3. Clic sur "Oui" → téléchargement automatique
4. Clic sur "Installer" → installation silencieuse + redémarrage
5. **C'est tout !**

## 🔒 Réduire les détections antivirus

### Solution immédiate (Gratuite)

1. **Soumettre à Microsoft Defender**
   - https://www.microsoft.com/en-us/wdsi/filesubmission
   - Soumettre l'installeur
   - Attendre analyse (~48h)

2. **Ajouter des métadonnées à l'exécutable**
   - Déjà fait via PyInstaller (nom, version, icône)

### Solution professionnelle (Payante mais recommandée)

**Signature de code** (~300-400€/an)

1. **Obtenir un certificat**
   - Sectigo Code Signing Certificate
   - DigiCert Code Signing Certificate
   - GlobalSign Code Signing

2. **Signer les fichiers**
   ```bash
   # Signer l'exécutable
   signtool sign /f certificat.pfx /p mot_de_passe /t http://timestamp.digicert.com dist\SupplierOrderManager.exe

   # Signer l'installeur
   signtool sign /f certificat.pfx /p mot_de_passe /t http://timestamp.digicert.com installer_output\SupplierOrderManager-Setup-v1.0.3.exe
   ```

3. **Avantages**
   - ✅ Windows Defender ne bloque plus
   - ✅ Affiche le nom de votre entreprise
   - ✅ Confiance immédiate des utilisateurs
   - ✅ Aucun avertissement "Éditeur inconnu"

## 📊 Cycle de vie d'une mise à jour

```
Développeur                    GitHub                    Utilisateur
    |                            |                            |
    |--1. Compile v1.0.4-------->|                            |
    |                            |                            |
    |--2. Crée installeur------->|                            |
    |                            |                            |
    |--3. Publie release-------->|                            |
    |                            |                            |
    |                            |<---4. App vérifie MAJ------|
    |                            |                            |
    |                            |---5. Nouvelle version---->|
    |                            |                            |
    |                            |<---6. Télécharge-----------|
    |                            |                            |
    |                            |---7. Envoie installeur--->|
    |                            |                            |
    |                            |    8. Installation auto    |
    |                            |    9. Redémarrage auto     |
    |                            |    ✅ À jour !             |
```

## 🎯 Checklist avant release

- [ ] Version incrémentée dans `app/version.py`
- [ ] Version incrémentée dans `installer.iss`
- [ ] Application compilée (`python build_exe.py`)
- [ ] Application testée localement
- [ ] Installeur créé (Inno Setup)
- [ ] Installeur testé
- [ ] Code commité et pushé sur GitHub
- [ ] Release GitHub créée avec tag vX.X.X
- [ ] Installeur uploadé dans la release
- [ ] Notes de release rédigées
- [ ] Release publiée

## 📝 Template notes de release

```markdown
## 🎉 v1.0.X - Titre de la release

### ✨ Nouvelles fonctionnalités
- Ajout de [fonctionnalité]
- Amélioration de [fonctionnalité]

### 🐛 Corrections
- Correction du bug [description]
- Fix de [problème]

### 🔧 Améliorations techniques
- Optimisation de [composant]
- Refactoring de [code]

### 📥 Installation

**Nouveaux utilisateurs** :
1. Téléchargez `SupplierOrderManager-Setup-v1.0.X.exe`
2. Exécutez l'installeur
3. Lancez l'application depuis le menu Démarrer

**Mise à jour automatique** :
Si vous utilisez déjà l'application, elle vous proposera automatiquement de mettre à jour.

**Mise à jour manuelle** :
1. Téléchargez `SupplierOrderManager-Setup-v1.0.X.exe`
2. Exécutez l'installeur (il désinstallera automatiquement l'ancienne version)
3. L'application sera mise à jour

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## 🆘 Dépannage

**L'application ne détecte pas les mises à jour**
- Vérifier la connexion Internet
- Vérifier que la release est publiée (pas en draft)
- Vérifier que l'installeur est bien nommé avec "Setup" dans le nom

**Windows Defender bloque l'installeur**
- Soumettre à Microsoft (lien ci-dessus)
- Demander aux utilisateurs d'ajouter une exception temporaire
- Envisager signature de code

**L'installeur ne désinstalle pas l'ancienne version**
- Vérifier que l'AppId dans `installer.iss` n'a pas changé
- Désinstaller manuellement depuis Paramètres Windows > Applications

## 📞 Support

Pour toute question :
- GitHub Issues : https://github.com/Oufdeladingue/supplier-order-manager/issues
- Documentation : Voir README.md
