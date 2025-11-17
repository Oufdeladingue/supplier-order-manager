# 📘 Guide d'utilisation quotidienne

Guide pratique pour utiliser l'application au quotidien.

## 🚀 Démarrage rapide

### Lancer l'application

**Méthode 1 : Double-clic**
- Double-cliquez sur `start_app.bat`

**Méthode 2 : Ligne de commande**
```powershell
cd C:\Users\mjardin\Desktop\supplier-order-manager
.\venv\Scripts\activate
python app\main.py
```

### Se connecter

1. Entrez votre email (celui créé dans Supabase)
2. Entrez votre mot de passe
3. Cliquez sur "Se connecter"

## 📋 Interface principale

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────┐
│ 🔄 Rafraîchir | 📁 Importer | 🚪 Déconnexion       │
├─────────────────────────────────────────────────────┤
│ Statut: [Tous ▼]  Date: [15/01/2024 📅] [Afficher tout] │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Date     | Fournisseur | Fichier      | Statut   │
│  ---------|-------------|--------------|----------|│
│  15/01/24 | Alpha       | cmd_15.csv   | À traiter│
│  15/01/24 | Beta        | order.xlsx   | En cours │
│  14/01/24 | Gamma       | cmd_14.csv   | Terminé  │
│                                                     │
├─────────────────────────────────────────────────────┤
│ 🔒 Verrouiller | ⚙️ Transformer | 🔓 Déverrouiller │
│ 📦 Regrouper   | 📜 Historique                     │
└─────────────────────────────────────────────────────┘
```

### Barre d'outils

- **🔄 Rafraîchir** : Recharge la liste des fichiers
- **📁 Importer** : Importe un fichier manuellement
- **🚪 Déconnexion** : Ferme la session

### Filtres

- **Statut** : Filtre par statut (À traiter, En cours, Terminé, Erreur)
- **Date** : Filtre par date de réception
- **Afficher tout** : Affiche tous les fichiers (toutes dates)

## 🔄 Workflow quotidien typique

### 1. Arrivée au bureau (10h15)

```
✅ Vérifier que la collecte automatique a fonctionné
```

1. Lancez l'application
2. Regardez la liste des fichiers du jour
3. Vous devriez voir ~15 fichiers avec le statut "À traiter"

**Si aucun fichier n'apparaît :**
- Vérifiez les logs : `logs/collector_*.log`
- Testez manuellement : `python worker\collector.py`

### 2. Traiter un fichier

```
Sélectionner → Verrouiller → Transformer → Déverrouiller
```

#### Étape par étape

1. **Sélectionner** : Cliquez sur une ligne dans le tableau
   - Le fichier est surligné
   - Les boutons s'activent

2. **Verrouiller** : Cliquez sur "🔒 Verrouiller"
   - Le statut passe à "En cours"
   - Votre nom apparaît dans "Verrouillé par"
   - Les autres utilisateurs voient que vous travaillez dessus

3. **Transformer** : Cliquez sur "⚙️ Transformer"
   - Les règles de transformation sont appliquées
   - Le fichier transformé est sauvegardé dans Supabase
   - Le statut passe à "Terminé"

4. **Déverrouiller** (si besoin) : Cliquez sur "🔓 Déverrouiller"
   - Le fichier redevient disponible
   - Utile si vous devez interrompre le traitement

### 3. Gérer les fichiers des jours précédents

Si des fichiers n'ont pas été traités :

1. Cliquez sur "Afficher tout"
2. Filtrez par fournisseur si besoin
3. Sélectionnez les fichiers non traités
4. Utilisez "📦 Regrouper" pour les fusionner

### 4. Consulter l'historique

Pour voir qui a fait quoi sur un fichier :

1. Sélectionnez le fichier
2. Cliquez sur "📜 Historique"
3. Vous voyez toutes les actions :
   - Qui a verrouillé quand
   - Qui a transformé quand
   - Erreurs éventuelles

## 🎯 Cas d'usage spécifiques

### Cas 1 : Fichier en erreur

**Symptôme :** Un fichier a le statut "Erreur"

**Solution :**
1. Vérifiez l'historique pour voir l'erreur
2. Téléchargez le fichier original depuis Supabase
3. Vérifiez le format
4. Si le fichier est valide, reverrouillez et re-transformez
5. Si le format est incorrect, contactez le fournisseur

### Cas 2 : Fichier manquant

**Symptôme :** Un fournisseur n'a pas envoyé son fichier

**Solution :**
1. Vérifiez l'heure (la collecte est à 10h)
2. Consultez les logs : `logs/collector_*.log`
3. Vérifiez la boîte mail/FTP manuellement
4. Si le fichier existe, importez-le manuellement :
   - Cliquez sur "📁 Importer"
   - Sélectionnez le fichier
   - Choisissez le fournisseur

### Cas 3 : Regrouper plusieurs jours

**Scenario :** Le fournisseur Alpha n'a pas envoyé lundi et mardi. Il envoie les 3 jours mercredi.

**Solution :**
1. Cliquez sur "Afficher tout"
2. Filtrez par fournisseur "Alpha"
3. Sélectionnez tous les fichiers à regrouper
4. Cliquez sur "📦 Regrouper"
5. Le fichier fusionné est créé

### Cas 4 : Collaborer avec un collègue

**Scenario :** Votre collègue travaille sur un fichier

**Ce que vous voyez :**
```
Date     | Fournisseur | Fichier      | Statut    | Verrouillé par
15/01/24 | Alpha       | cmd_15.csv   | En cours  | Marie Dupont
```

**Actions possibles :**
- ✅ Voir qu'il est en cours de traitement
- ✅ Consulter l'historique
- ❌ Vous ne pouvez pas le modifier (verrouillé)

**Quand votre collègue a fini :**
- Le statut passe à "Terminé"
- "Traité par" affiche son nom
- Le verrou est levé

## 🔍 Comprendre les statuts

| Statut | Signification | Actions possibles |
|--------|---------------|-------------------|
| 📝 **À traiter** | Fichier collecté, pas encore traité | Verrouiller, Historique |
| ⏳ **En cours** | Quelqu'un travaille dessus | Transformer (si vous), Déverrouiller (si vous), Historique |
| ✅ **Terminé** | Traitement terminé | Historique |
| ❌ **Erreur** | Erreur lors du traitement | Historique, Re-traiter |
| 📦 **Regroupé** | Fichier fusionné avec d'autres | Historique |

## 💡 Astuces et bonnes pratiques

### Astuces d'utilisation

1. **Rafraîchissement automatique**
   - L'application se rafraîchit toutes les 30 secondes
   - Vous voyez les changements des autres utilisateurs en temps réel

2. **Filtres intelligents**
   - Utilisez "À traiter" pour voir votre travail du jour
   - Utilisez "Afficher tout" + filtre fournisseur pour les retards

3. **Ordre de traitement**
   - Traitez d'abord les fichiers du jour
   - Puis gérez les retards avec "Regrouper"

### Bonnes pratiques

#### ✅ À FAIRE

- Vérifier chaque matin que la collecte a fonctionné
- Déverrouiller un fichier si vous l'interrompez
- Consulter l'historique en cas de doute
- Regrouper les fichiers anciens avant traitement

#### ❌ À ÉVITER

- Laisser un fichier verrouillé sans le traiter
- Fermer l'application avec des fichiers verrouillés
- Traiter deux fois le même fichier
- Ignorer les fichiers en erreur

### Gestion des verrous

**Verrous automatiques :**
- Un verrou est automatiquement levé après 30 minutes d'inactivité
- Empêche les blocages si quelqu'un oublie de déverrouiller

**Forcer le déverrouillage :**
Si un collègue a laissé un verrou par erreur :
1. Attendez 30 minutes (levée automatique)
2. Ou demandez-lui de déverrouiller
3. En dernier recours, contactez l'administrateur

## 📊 Suivi et reporting

### Voir votre activité

1. Filtrez par statut "Terminé"
2. Les fichiers avec votre nom dans "Traité par" sont les vôtres
3. Consultez l'historique pour les détails

### Voir l'activité globale

1. Cliquez sur "Afficher tout"
2. Regardez la colonne "Traité par"
3. Vous voyez qui a traité quoi

### Statistiques

Pour l'instant, les stats sont à calculer manuellement. Dans une future version :
- Dashboard avec graphiques
- Export de rapports
- Alertes automatiques

## 🆘 Problèmes fréquents

### L'application ne se lance pas

1. Vérifiez que l'environnement virtuel est activé
2. Consultez les logs : `logs/app_*.log`
3. Réinstallez les dépendances : `pip install -r requirements.txt`

### Erreur de connexion

1. Vérifiez vos identifiants
2. Vérifiez Internet
3. Vérifiez que Supabase est accessible

### Fichier ne se transforme pas

1. Consultez l'historique du fichier
2. Vérifiez les règles dans `config/transformations.json`
3. Testez le fichier manuellement

### Autre utilisateur ne voit pas mes changements

1. Attendez 30 secondes (auto-refresh)
2. Demandez-lui de cliquer sur "🔄 Rafraîchir"
3. Vérifiez qu'il est connecté au même projet Supabase

## 🔧 Maintenance

### Quotidienne

- Lancer l'application
- Vérifier que la collecte a fonctionné
- Traiter les fichiers du jour

### Hebdomadaire

- Vérifier les fichiers en erreur
- Regrouper les fichiers anciens
- Nettoyer le dossier `temp/`

### Mensuelle

- Archiver les anciens logs
- Vérifier l'espace disque Supabase
- Mettre à jour les règles de transformation si besoin

## 📞 Support

### Auto-diagnostic

1. Consultez les logs dans `logs/`
2. Vérifiez la connexion Internet
3. Testez avec un collègue si c'est collaboratif

### Escalade

Si le problème persiste :
1. Notez l'erreur exacte
2. Consultez le `README.md`
3. Vérifiez la configuration dans `.env`

---

🎉 **Bon courage pour vos traitements quotidiens !**
