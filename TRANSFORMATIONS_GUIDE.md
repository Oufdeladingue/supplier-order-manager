# 🔄 Guide de configuration des transformations

Ce guide explique comment configurer les règles de transformation pour chaque fournisseur.

## 📋 Comprendre les transformations

Chaque fournisseur envoie ses fichiers dans un format différent. Les transformations permettent de :
- Renommer les colonnes pour uniformiser
- Ajouter des colonnes manquantes
- Supprimer des colonnes inutiles
- Formater les valeurs (majuscules, nombres, dates, etc.)

## 🎯 Structure d'une transformation

Dans `config/transformations.json` :

```json
{
  "transformations": {
    "transform_nom_fournisseur": {
      "description": "Description de la transformation",
      "column_mapping": { },
      "columns_to_add": { },
      "columns_to_remove": [ ],
      "format_rules": { }
    }
  }
}
```

## 📊 1. Column Mapping (Renommage)

Permet de renommer les colonnes pour avoir un format uniforme.

### Exemple

Le fournisseur A utilise "Ref" mais vous voulez "product_ref" :

```json
"column_mapping": {
  "Ref": "product_ref",
  "Qté": "quantity",
  "Prix U.": "unit_price",
  "Désignation": "description"
}
```

### Cas pratiques

#### Colonnes avec espaces ou accents
```json
"column_mapping": {
  "Référence Produit": "product_ref",
  "Prix TTC €": "price_ttc",
  "N° Commande": "order_number"
}
```

#### Colonnes en anglais vers français
```json
"column_mapping": {
  "SKU": "reference",
  "Qty": "quantite",
  "Description": "designation"
}
```

## ➕ 2. Columns to Add (Ajout de colonnes)

Ajoute des colonnes qui manquent dans le fichier fournisseur.

### Valeurs spéciales

- `"today"` : Date du jour (YYYY-MM-DD)
- `"now"` : Date et heure actuelles
- Tout autre texte : Valeur fixe

### Exemples

```json
"columns_to_add": {
  "date_commande": "today",
  "timestamp_import": "now",
  "statut": "nouveau",
  "fournisseur": "ALPHA",
  "type_commande": "quotidienne"
}
```

### Cas d'usage

#### Ajouter la date de traitement
```json
"columns_to_add": {
  "date_import": "today"
}
```

#### Ajouter des métadonnées
```json
"columns_to_add": {
  "source": "fichier_fournisseur",
  "version": "v1",
  "validé": "non"
}
```

## ➖ 3. Columns to Remove (Suppression)

Supprime les colonnes inutiles du fichier fournisseur.

### Exemples

```json
"columns_to_remove": [
  "Colonne vide",
  "Notes internes",
  "Champ obsolète",
  "ID temporaire"
]
```

### Cas pratiques

#### Supprimer les colonnes de calcul
```json
"columns_to_remove": [
  "Total TTC",
  "Total HT",
  "TVA",
  "Remise calculée"
]
```

#### Supprimer les colonnes d'export
```json
"columns_to_remove": [
  "Export ID",
  "Timestamp",
  "User"
]
```

## 🎨 4. Format Rules (Formatage)

Applique des transformations sur les valeurs des colonnes.

### Types de formatage disponibles

| Type | Description | Exemple |
|------|-------------|---------|
| `uppercase` | Tout en MAJUSCULES | "abc" → "ABC" |
| `lowercase` | Tout en minuscules | "ABC" → "abc" |
| `integer` | Convertit en nombre entier | "12.5" → 12 |
| `float` | Convertit en nombre décimal | "12,50" → 12.50 |
| `date` | Convertit en date | "01/12/2024" → 2024-12-01 |
| `trim` | Supprime les espaces | " abc " → "abc" |

### Exemples

```json
"format_rules": {
  "product_ref": "uppercase",
  "email": "lowercase",
  "quantity": "integer",
  "unit_price": "float",
  "order_date": "date",
  "description": "trim"
}
```

### Cas pratiques

#### Uniformiser les références produits
```json
"format_rules": {
  "product_ref": "uppercase",
  "ean": "trim"
}
```

#### Nettoyer les nombres
```json
"format_rules": {
  "quantity": "integer",
  "price_ht": "float",
  "price_ttc": "float",
  "discount_percent": "float"
}
```

## 📝 Exemples complets par scénario

### Scénario 1 : Fournisseur avec fichier CSV simple

**Fichier reçu :**
```
Ref,Qté,Prix
ABC123,10,25.50
DEF456,5,12.00
```

**Fichier souhaité :**
```
product_ref,quantity,unit_price,date_commande,fournisseur
ABC123,10,25.50,2024-01-15,ALPHA
DEF456,5,12.00,2024-01-15,ALPHA
```

**Configuration :**
```json
{
  "transform_alpha": {
    "description": "Transformation fichier Fournisseur Alpha",
    "column_mapping": {
      "Ref": "product_ref",
      "Qté": "quantity",
      "Prix": "unit_price"
    },
    "columns_to_add": {
      "date_commande": "today",
      "fournisseur": "ALPHA"
    },
    "columns_to_remove": [],
    "format_rules": {
      "product_ref": "uppercase",
      "quantity": "integer",
      "unit_price": "float"
    }
  }
}
```

### Scénario 2 : Fournisseur avec fichier Excel complexe

**Fichier reçu :**
```
Référence Produit | Désignation | Qté commandée | Prix U. HT | TVA | Notes
  abc-123        | Produit A   |     10       | 25,50 €    | 20% | Note
  def-456        | Produit B   |     5        | 12,00 €    | 20% | -
```

**Fichier souhaité :**
```
product_ref,description,quantity,unit_price,date_import
ABC-123,Produit A,10,25.50,2024-01-15
DEF-456,Produit B,5,12.00,2024-01-15
```

**Configuration :**
```json
{
  "transform_beta": {
    "description": "Transformation fichier Fournisseur Beta",
    "column_mapping": {
      "Référence Produit": "product_ref",
      "Désignation": "description",
      "Qté commandée": "quantity",
      "Prix U. HT": "unit_price"
    },
    "columns_to_add": {
      "date_import": "today"
    },
    "columns_to_remove": [
      "TVA",
      "Notes"
    ],
    "format_rules": {
      "product_ref": "uppercase",
      "product_ref": "trim",
      "description": "trim",
      "quantity": "integer",
      "unit_price": "float"
    }
  }
}
```

### Scénario 3 : Fournisseur avec format anglo-saxon

**Fichier reçu :**
```
SKU,Product Name,Order Qty,Unit Price USD,Ship Date
SKU001,Widget A,100,15.99,12/31/2024
SKU002,Widget B,50,29.99,12/31/2024
```

**Fichier souhaité :**
```
reference,nom_produit,quantite,prix_unitaire,date_expedition
SKU001,Widget A,100,15.99,2024-12-31
SKU002,Widget B,50,29.99,2024-12-31
```

**Configuration :**
```json
{
  "transform_gamma": {
    "description": "Transformation fichier Fournisseur Gamma (US)",
    "column_mapping": {
      "SKU": "reference",
      "Product Name": "nom_produit",
      "Order Qty": "quantite",
      "Unit Price USD": "prix_unitaire",
      "Ship Date": "date_expedition"
    },
    "columns_to_add": {},
    "columns_to_remove": [],
    "format_rules": {
      "reference": "uppercase",
      "quantite": "integer",
      "prix_unitaire": "float",
      "date_expedition": "date"
    }
  }
}
```

## 🛠️ Workflow de configuration

### 1. Analyser le fichier fournisseur

1. Récupérez un fichier exemple du fournisseur
2. Ouvrez-le dans Excel/LibreOffice
3. Notez :
   - Les noms de colonnes
   - Le format des données
   - Les colonnes inutiles
   - Ce qui manque

### 2. Définir le format cible

Décidez du format uniforme que vous voulez pour tous les fournisseurs.

Exemple de standard interne :
```
product_ref | description | quantity | unit_price | date_commande
```

### 3. Créer la transformation

1. Ouvrez `config/transformations.json`
2. Copiez un exemple existant
3. Adaptez-le pour votre fournisseur
4. Testez avec l'application

### 4. Tester et ajuster

1. Importez un fichier test
2. Verrouillez-le
3. Transformez-le
4. Vérifiez le résultat
5. Ajustez si nécessaire

## ⚠️ Pièges à éviter

### Noms de colonnes avec espaces

❌ Incorrect :
```json
"column_mapping": {
  "Ref Produit": "product ref"
}
```

✅ Correct :
```json
"column_mapping": {
  "Ref Produit": "product_ref"
}
```

### Ordre des transformations

Les transformations sont appliquées dans cet ordre :
1. column_mapping (renommage)
2. columns_to_add (ajout)
3. columns_to_remove (suppression)
4. format_rules (formatage)

Donc utilisez les NOUVEAUX noms dans `format_rules` :

❌ Incorrect :
```json
"column_mapping": {
  "Ref": "product_ref"
},
"format_rules": {
  "Ref": "uppercase"  // ❌ Cette colonne n'existe plus !
}
```

✅ Correct :
```json
"column_mapping": {
  "Ref": "product_ref"
},
"format_rules": {
  "product_ref": "uppercase"  // ✅ Nouveau nom
}
```

## 🧪 Tester vos transformations

### Test manuel dans l'application

1. Lancez l'application
2. Importez un fichier test
3. Verrouillez-le
4. Cliquez sur "Transformer"
5. Vérifiez le résultat dans Supabase Storage

### Test avec Python

Créez un script `test_transformation.py` :

```python
from app.services.file_processor import FileProcessor
from app.models.file_record import FileType
import json

# Charger les règles
with open('config/transformations.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

# Tester une transformation
processor = FileProcessor()
df = processor.read_file('test_file.csv', FileType.CSV)
transformed = processor.apply_transformation(df, rules['transformations']['transform_alpha'])

print(transformed.head())
print(transformed.columns)
```

## 📞 Besoin d'aide ?

Si vous n'arrivez pas à configurer une transformation :
1. Vérifiez les logs dans `logs/`
2. Testez étape par étape (mapping, puis ajout, puis formatage)
3. Consultez les exemples dans ce guide

---

💡 **Conseil** : Commencez simple avec juste le `column_mapping`, testez, puis ajoutez progressivement les autres règles.
