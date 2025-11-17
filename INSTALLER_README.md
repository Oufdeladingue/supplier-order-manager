# Instructions pour créer l'installeur

## Prérequis

1. **Installer Inno Setup** : https://jrsoftware.org/isinfo.php
   - Téléchargez et installez Inno Setup 6.x (gratuit)

## Étapes pour créer l'installeur

### 1. Compiler l'exécutable

```bash
python build_exe.py
```

Cela va créer `dist/SupplierOrderManager.exe`

### 2. Compiler l'installeur

**Option A : Via l'interface Inno Setup**
1. Lancez Inno Setup Compiler
2. Ouvrez le fichier `installer.iss`
3. Cliquez sur "Build" (F9) ou "Build > Compile"

**Option B : En ligne de commande**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### 3. Résultat

L'installeur sera créé dans le dossier `installer_output/` :
- `SupplierOrderManager-Setup-v1.0.3.exe`

## Fonctionnalités de l'installeur

✅ **Installation propre**
- Installe dans `C:\Program Files\Gestionnaire Commandes Fournisseurs\`
- Crée un raccourci dans le menu Démarrer
- Option de raccourci sur le bureau

✅ **Mise à jour intelligente**
- Détecte automatiquement une version précédente
- Propose de désinstaller avant d'installer la nouvelle version
- Vérifie si l'application est en cours d'exécution

✅ **Désinstallation propre**
- Désinstalleur automatiquement créé
- Suppression complète de tous les fichiers
- Suppression des raccourcis

✅ **Installation silencieuse**
- Support des paramètres `/SILENT` et `/VERYSILENT`
- Parfait pour les déploiements automatiques

## Paramètres de ligne de commande

```bash
# Installation silencieuse
SupplierOrderManager-Setup-v1.0.3.exe /SILENT

# Installation très silencieuse (aucun dialogue)
SupplierOrderManager-Setup-v1.0.3.exe /VERYSILENT

# Installation avec log
SupplierOrderManager-Setup-v1.0.3.exe /LOG="C:\install.log"

# Installation sans créer de raccourci bureau
SupplierOrderManager-Setup-v1.0.3.exe /TASKS="!desktopicon"
```

## Distribution

Une fois l'installeur créé :
1. Créez une release GitHub (v1.0.3)
2. Uploadez l'installeur (`SupplierOrderManager-Setup-v1.0.3.exe`)
3. L'application pourra détecter et télécharger automatiquement les mises à jour

## Signature de code (Optionnel mais recommandé)

Pour éviter les avertissements Windows Defender :

1. **Obtenir un certificat de signature de code**
   - DigiCert, Sectigo, GlobalSign (~300-400€/an)

2. **Signer l'exécutable**
   ```bash
   signtool sign /f "certificat.pfx" /p "mot_de_passe" /t http://timestamp.digicert.com dist\SupplierOrderManager.exe
   ```

3. **Signer l'installeur**
   ```bash
   signtool sign /f "certificat.pfx" /p "mot_de_passe" /t http://timestamp.digicert.com installer_output\SupplierOrderManager-Setup-v1.0.3.exe
   ```

## Dépannage

**Erreur : "Inno Setup introuvable"**
- Vérifiez que Inno Setup est installé
- Ajoutez le chemin d'installation à votre PATH

**L'installeur ne se lance pas**
- Vérifiez les permissions (exécuter en tant qu'administrateur)
- Désactivez temporairement l'antivirus

**Erreur lors de la compilation**
- Vérifiez que tous les fichiers sources existent
- Vérifiez le chemin de l'icône dans `installer.iss`
