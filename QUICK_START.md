# ⚡ Quick Start - Démarrage rapide

Guide ultra-rapide pour démarrer en 15 minutes.

## 📦 Installation express

### 1. Python (2 min)

```powershell
# Téléchargez Python 3.11+ sur python.org
# ⚠️ Cochez "Add to PATH" lors de l'installation
```

### 2. Dépendances (3 min)

```powershell
cd C:\Users\mjardin\Desktop\supplier-order-manager
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Supabase (5 min)

1. Allez sur [supabase.com](https://supabase.com)
2. **SQL Editor** → Copiez/collez `config/supabase_schema.sql` → Run
3. **Storage** → Créez 2 buckets : `supplier-files-original` et `supplier-files-transformed`
4. **Authentication** → Créez 2 utilisateurs
5. **Settings** → **API** → Copiez URL et clés

### 4. Configuration (3 min)

Créez `.env` (copiez `.env.example`) :

```env
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-anon-key
SUPABASE_SERVICE_KEY=votre-service-key

EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=votre@email.com
EMAIL_PASSWORD=votre-mot-de-passe

# Reste des configs...
```

### 5. Test (2 min)

```powershell
python app\main.py
```

✅ Vous devriez voir l'écran de connexion !

---

## 🎯 Commandes essentielles

### Lancer l'application

```powershell
# Méthode 1 : Double-clic
start_app.bat

# Méthode 2 : Ligne de commande
.\venv\Scripts\activate
python app\main.py
```

### Tester la collecte

```powershell
python worker\collector.py
```

### Configurer la tâche planifiée

```powershell
# En administrateur
cd worker
.\setup_scheduler.bat
```

### Voir les logs

```powershell
# Logs de l'app
type logs\app_*.log | more

# Logs du collector
type logs\collector_*.log | more
```

---

## 📝 Configuration minimale

### Ajouter un fournisseur

Éditez `config/suppliers.json` :

```json
{
  "id": "FOURNISSEUR_001",
  "name": "Mon Fournisseur",
  "email_pattern": "commandes@fournisseur.com",
  "file_patterns": ["*.csv"],
  "active": true,
  "source": "email",
  "transformation_id": "transform_001"
}
```

### Ajouter une transformation

Éditez `config/transformations.json` :

```json
"transform_001": {
  "description": "Transformation Fournisseur 1",
  "column_mapping": {
    "Ref": "product_ref",
    "Qté": "quantity"
  },
  "columns_to_add": {
    "date_commande": "today"
  },
  "columns_to_remove": [],
  "format_rules": {
    "product_ref": "uppercase",
    "quantity": "integer"
  }
}
```

---

## 🚀 Workflow quotidien

1. **10h** : Collecte automatique
2. **10h15** : Lancez l'app → Vérifiez que les fichiers sont là
3. Pour chaque fichier :
   - Sélectionnez
   - Cliquez "🔒 Verrouiller"
   - Cliquez "⚙️ Transformer"
4. Fichier traité !

---

## 🔧 Checklist première utilisation

- [ ] Python installé et dans PATH
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées
- [ ] Supabase configuré (DB + Storage + Auth)
- [ ] Fichier `.env` créé et rempli
- [ ] Au moins 1 fournisseur dans `suppliers.json`
- [ ] Au moins 1 transformation dans `transformations.json`
- [ ] Test de connexion OK
- [ ] Tâche planifiée configurée (sur 1 seul poste)

---

## 🆘 Dépannage rapide

| Problème | Solution rapide |
|----------|-----------------|
| "Python not found" | Ajoutez Python au PATH |
| "Module not found" | `pip install -r requirements.txt` |
| "Supabase error" | Vérifiez URL et clés dans `.env` |
| "Email error" | Gmail = utilisez App Password |
| App ne lance pas | Vérifiez `logs/app_*.log` |
| Pas de fichiers | Vérifiez `logs/collector_*.log` |

---

## 📚 Documentation complète

- 📖 [README.md](README.md) - Documentation principale
- 🔧 [INSTALLATION.md](INSTALLATION.md) - Installation détaillée
- 🎮 [USAGE.md](USAGE.md) - Guide d'utilisation
- 🔄 [TRANSFORMATIONS_GUIDE.md](TRANSFORMATIONS_GUIDE.md) - Guide des transformations
- 📋 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Vue d'ensemble du projet

---

## 💡 Tips

- Utilisez `start_app.bat` pour lancer rapidement
- Logs dans `logs/` pour debug
- Rafraîchissement auto toutes les 30s
- Verrous auto-levés après 30 min
- Transformation = renommage + ajout + suppression + formatage

---

🎉 **C'est parti !**

Besoin de plus de détails ? → [README.md](README.md)
