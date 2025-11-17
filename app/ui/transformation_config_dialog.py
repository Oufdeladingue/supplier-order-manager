"""
Interface de configuration des transformations de fichiers fournisseurs
"""

import sys
import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QGroupBox, QLineEdit, QTextEdit, QHeaderView, QTabWidget,
    QWidget, QFileDialog, QSplitter
)
from PySide6.QtCore import Qt, Signal

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.file_processor import FileProcessor


class TransformationConfigDialog(QDialog):
    """
    Dialogue de configuration des règles de transformation
    """

    transformation_saved = Signal(str)  # Signal émis quand une transformation est sauvegardée

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_processor = FileProcessor()
        self.current_supplier_id = None
        self.current_transformation = None
        self.test_file_path = None
        self.test_dataframe = None

        self.init_ui()
        self.load_suppliers()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Configuration des Transformations")
        self.setGeometry(100, 100, 1400, 900)

        layout = QVBoxLayout(self)

        # Section sélection fournisseur
        supplier_section = self.create_supplier_section()
        layout.addWidget(supplier_section)

        # Onglets pour les différentes sections
        tabs = QTabWidget()

        # Onglet 1: Aperçu fichier source
        tab_preview = self.create_preview_tab()
        tabs.addTab(tab_preview, "📄 Aperçu Fichier Source")

        # Onglet 2: Mapping des colonnes
        tab_mapping = self.create_mapping_tab()
        tabs.addTab(tab_mapping, "🔄 Mapping Colonnes")

        # Onglet 3: Colonnes à ajouter
        tab_add = self.create_add_columns_tab()
        tabs.addTab(tab_add, "➕ Ajouter Colonnes")

        # Onglet 4: Colonnes à supprimer
        tab_remove = self.create_remove_columns_tab()
        tabs.addTab(tab_remove, "➖ Supprimer Colonnes")

        # Onglet 5: Formatage
        tab_format = self.create_format_tab()
        tabs.addTab(tab_format, "✨ Formatage")

        # Onglet 6: Test de la transformation
        tab_test = self.create_test_tab()
        tabs.addTab(tab_test, "🧪 Test Transformation")

        layout.addWidget(tabs)

        # Boutons de validation
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Sauvegarder Transformation")
        self.save_btn.clicked.connect(self.save_transformation)
        self.save_btn.setEnabled(False)

        self.cancel_btn = QPushButton("❌ Fermer")
        self.cancel_btn.clicked.connect(self.close)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def create_supplier_section(self) -> QGroupBox:
        """Crée la section de sélection du fournisseur"""
        group = QGroupBox("Sélection Fournisseur")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Fournisseur:"))

        self.supplier_combo = QComboBox()
        self.supplier_combo.currentTextChanged.connect(self.on_supplier_changed)
        layout.addWidget(self.supplier_combo, stretch=1)

        self.load_sample_btn = QPushButton("📥 Charger fichier exemple")
        self.load_sample_btn.clicked.connect(self.load_sample_file)
        layout.addWidget(self.load_sample_btn)

        self.load_existing_btn = QPushButton("📂 Charger config existante")
        self.load_existing_btn.clicked.connect(self.load_existing_transformation)
        layout.addWidget(self.load_existing_btn)

        group.setLayout(layout)
        return group

    def create_preview_tab(self) -> QWidget:
        """Crée l'onglet d'aperçu du fichier source"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Info fichier
        info_layout = QHBoxLayout()
        self.file_info_label = QLabel("Aucun fichier chargé")
        info_layout.addWidget(self.file_info_label)
        layout.addLayout(info_layout)

        # Tableau d'aperçu
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.preview_table)

        return widget

    def create_mapping_tab(self) -> QWidget:
        """Crée l'onglet de mapping des colonnes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel(
            "Définissez comment renommer les colonnes existantes.\n"
            "Format: Colonne Source → Nouveau Nom"
        ))

        # Boutons d'action
        btn_layout = QHBoxLayout()

        add_mapping_btn = QPushButton("➕ Ajouter un mapping")
        add_mapping_btn.clicked.connect(self.add_mapping_row)
        btn_layout.addWidget(add_mapping_btn)

        remove_mapping_btn = QPushButton("➖ Supprimer sélection")
        remove_mapping_btn.clicked.connect(self.remove_mapping_row)
        btn_layout.addWidget(remove_mapping_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tableau de mapping
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["Colonne Source", "Nouveau Nom"])
        self.mapping_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.mapping_table)

        return widget

    def create_add_columns_tab(self) -> QWidget:
        """Crée l'onglet d'ajout de colonnes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel(
            "Définissez les nouvelles colonnes à ajouter avec leur valeur par défaut.\n"
            "Format: Nom Colonne → Valeur"
        ))

        # Boutons d'action
        btn_layout = QHBoxLayout()

        add_column_btn = QPushButton("➕ Ajouter une colonne")
        add_column_btn.clicked.connect(self.add_column_row)
        btn_layout.addWidget(add_column_btn)

        remove_column_btn = QPushButton("➖ Supprimer sélection")
        remove_column_btn.clicked.connect(self.remove_column_row)
        btn_layout.addWidget(remove_column_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tableau d'ajout
        self.add_columns_table = QTableWidget()
        self.add_columns_table.setColumnCount(2)
        self.add_columns_table.setHorizontalHeaderLabels(["Nom Colonne", "Valeur"])
        self.add_columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.add_columns_table)

        return widget

    def create_remove_columns_tab(self) -> QWidget:
        """Crée l'onglet de suppression de colonnes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel(
            "Sélectionnez les colonnes à supprimer du fichier final.\n"
            "Une colonne par ligne."
        ))

        # Boutons d'action
        btn_layout = QHBoxLayout()

        add_remove_btn = QPushButton("➕ Ajouter une colonne à supprimer")
        add_remove_btn.clicked.connect(self.add_remove_row)
        btn_layout.addWidget(add_remove_btn)

        remove_remove_btn = QPushButton("➖ Supprimer sélection")
        remove_remove_btn.clicked.connect(self.remove_remove_row)
        btn_layout.addWidget(remove_remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tableau de suppression
        self.remove_columns_table = QTableWidget()
        self.remove_columns_table.setColumnCount(1)
        self.remove_columns_table.setHorizontalHeaderLabels(["Colonne à Supprimer"])
        self.remove_columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.remove_columns_table)

        return widget

    def create_format_tab(self) -> QWidget:
        """Crée l'onglet de formatage"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel(
            "Définissez les règles de formatage pour les colonnes.\n"
            "Format: Colonne → Type (uppercase/lowercase/date/number/trim)"
        ))

        # Boutons d'action
        btn_layout = QHBoxLayout()

        add_format_btn = QPushButton("➕ Ajouter un formatage")
        add_format_btn.clicked.connect(self.add_format_row)
        btn_layout.addWidget(add_format_btn)

        remove_format_btn = QPushButton("➖ Supprimer sélection")
        remove_format_btn.clicked.connect(self.remove_format_row)
        btn_layout.addWidget(remove_format_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Tableau de formatage
        self.format_table = QTableWidget()
        self.format_table.setColumnCount(2)
        self.format_table.setHorizontalHeaderLabels(["Colonne", "Type de Formatage"])
        self.format_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.format_table)

        return widget

    def create_test_tab(self) -> QWidget:
        """Crée l'onglet de test de transformation"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Bouton de test
        test_btn_layout = QHBoxLayout()

        self.test_btn = QPushButton("🧪 Tester la Transformation")
        self.test_btn.clicked.connect(self.test_transformation)
        self.test_btn.setEnabled(False)
        test_btn_layout.addWidget(self.test_btn)

        test_btn_layout.addStretch()
        layout.addLayout(test_btn_layout)

        # Résultat du test
        self.test_result_label = QLabel("Aucun test effectué")
        layout.addWidget(self.test_result_label)

        # Tableau du résultat
        self.test_result_table = QTableWidget()
        self.test_result_table.setAlternatingRowColors(True)
        layout.addWidget(self.test_result_table)

        return widget

    def load_suppliers(self):
        """Charge la liste des fournisseurs depuis le fichier de config"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "suppliers.json"

            if not config_path.exists():
                QMessageBox.warning(self, "Erreur", "Fichier suppliers.json introuvable")
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.supplier_combo.clear()
            self.supplier_combo.addItem("-- Sélectionner un fournisseur --", None)

            for supplier in config.get('suppliers', []):
                self.supplier_combo.addItem(
                    supplier['name'],
                    supplier['id']
                )

        except Exception as e:
            logger.error(f"Erreur chargement fournisseurs: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement fournisseurs:\n{str(e)}")

    def on_supplier_changed(self, text: str):
        """Appelé quand le fournisseur change"""
        supplier_id = self.supplier_combo.currentData()

        if supplier_id:
            self.current_supplier_id = supplier_id
            self.save_btn.setEnabled(True)
            self.load_sample_btn.setEnabled(True)
            self.load_existing_btn.setEnabled(True)
        else:
            self.current_supplier_id = None
            self.save_btn.setEnabled(False)
            self.load_sample_btn.setEnabled(False)
            self.load_existing_btn.setEnabled(False)

    def load_sample_file(self):
        """Charge un fichier exemple pour analyse"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier exemple",
            "",
            "Fichiers CSV (*.csv);;Fichiers Excel (*.xlsx *.xls)"
        )

        if not file_path:
            return

        try:
            # Lire le fichier
            self.test_file_path = file_path
            df = self.file_processor.read_file(file_path)
            self.test_dataframe = df

            # Afficher dans le tableau d'aperçu
            self.display_dataframe_preview(df)

            # Activer le bouton de test
            self.test_btn.setEnabled(True)

            # Info fichier
            self.file_info_label.setText(
                f"Fichier: {Path(file_path).name} | "
                f"Lignes: {len(df)} | "
                f"Colonnes: {len(df.columns)}"
            )

            QMessageBox.information(
                self,
                "Fichier chargé",
                f"Fichier chargé avec succès!\n"
                f"Lignes: {len(df)}\n"
                f"Colonnes: {', '.join(df.columns)}"
            )

        except Exception as e:
            logger.error(f"Erreur chargement fichier: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement fichier:\n{str(e)}")

    def display_dataframe_preview(self, df, max_rows: int = 20):
        """Affiche un aperçu du dataframe dans le tableau"""
        self.preview_table.clear()

        # Limiter le nombre de lignes affichées
        preview_df = df.head(max_rows)

        # Configuration du tableau
        self.preview_table.setRowCount(len(preview_df))
        self.preview_table.setColumnCount(len(preview_df.columns))
        self.preview_table.setHorizontalHeaderLabels(list(preview_df.columns))

        # Remplir le tableau
        for i, row in preview_df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.preview_table.setItem(i, j, item)

        self.preview_table.resizeColumnsToContents()

    def load_existing_transformation(self):
        """Charge une transformation existante"""
        if not self.current_supplier_id:
            QMessageBox.warning(self, "Attention", "Sélectionnez d'abord un fournisseur")
            return

        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "transformations.json"

            if not config_path.exists():
                QMessageBox.information(
                    self,
                    "Info",
                    "Aucune transformation existante trouvée.\n"
                    "Créez-en une nouvelle."
                )
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Chercher la transformation pour ce fournisseur
            transformation_id = f"transform_{self.current_supplier_id}"
            transformation = None

            for trans in config.get('transformations', []):
                if trans.get('id') == transformation_id:
                    transformation = trans
                    break

            if not transformation:
                QMessageBox.information(
                    self,
                    "Info",
                    f"Aucune transformation trouvée pour {self.current_supplier_id}.\n"
                    "Créez-en une nouvelle."
                )
                return

            # Charger la transformation
            self.current_transformation = transformation
            self.populate_ui_from_transformation(transformation)

            QMessageBox.information(self, "Succès", "Transformation chargée avec succès!")

        except Exception as e:
            logger.error(f"Erreur chargement transformation: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")

    def populate_ui_from_transformation(self, transformation: Dict):
        """Remplit l'interface avec les données de la transformation"""
        # Mapping
        self.mapping_table.setRowCount(0)
        mapping = transformation.get('column_mapping', {})
        for old_col, new_col in mapping.items():
            self.add_mapping_row(old_col, new_col)

        # Ajout de colonnes
        self.add_columns_table.setRowCount(0)
        add_cols = transformation.get('columns_to_add', {})
        for col_name, value in add_cols.items():
            self.add_column_row(col_name, value)

        # Suppression de colonnes
        self.remove_columns_table.setRowCount(0)
        remove_cols = transformation.get('columns_to_remove', [])
        for col_name in remove_cols:
            self.add_remove_row(col_name)

        # Formatage
        self.format_table.setRowCount(0)
        formatting = transformation.get('formatting', {})
        for col_name, format_type in formatting.items():
            self.add_format_row(col_name, format_type)

    # Méthodes d'ajout de lignes aux tableaux

    def add_mapping_row(self, old_col: str = "", new_col: str = ""):
        """Ajoute une ligne au tableau de mapping"""
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        self.mapping_table.setItem(row, 0, QTableWidgetItem(old_col))
        self.mapping_table.setItem(row, 1, QTableWidgetItem(new_col))

    def remove_mapping_row(self):
        """Supprime la ligne sélectionnée du tableau de mapping"""
        current_row = self.mapping_table.currentRow()
        if current_row >= 0:
            self.mapping_table.removeRow(current_row)

    def add_column_row(self, col_name: str = "", value: str = ""):
        """Ajoute une ligne au tableau d'ajout de colonnes"""
        row = self.add_columns_table.rowCount()
        self.add_columns_table.insertRow(row)
        self.add_columns_table.setItem(row, 0, QTableWidgetItem(col_name))
        self.add_columns_table.setItem(row, 1, QTableWidgetItem(value))

    def remove_column_row(self):
        """Supprime la ligne sélectionnée du tableau d'ajout"""
        current_row = self.add_columns_table.currentRow()
        if current_row >= 0:
            self.add_columns_table.removeRow(current_row)

    def add_remove_row(self, col_name: str = ""):
        """Ajoute une ligne au tableau de suppression de colonnes"""
        row = self.remove_columns_table.rowCount()
        self.remove_columns_table.insertRow(row)
        self.remove_columns_table.setItem(row, 0, QTableWidgetItem(col_name))

    def remove_remove_row(self):
        """Supprime la ligne sélectionnée du tableau de suppression"""
        current_row = self.remove_columns_table.currentRow()
        if current_row >= 0:
            self.remove_columns_table.removeRow(current_row)

    def add_format_row(self, col_name: str = "", format_type: str = ""):
        """Ajoute une ligne au tableau de formatage"""
        row = self.format_table.rowCount()
        self.format_table.insertRow(row)
        self.format_table.setItem(row, 0, QTableWidgetItem(col_name))

        # ComboBox pour le type de formatage
        format_combo = QComboBox()
        format_combo.addItems(["uppercase", "lowercase", "date", "number", "trim"])
        if format_type:
            index = format_combo.findText(format_type)
            if index >= 0:
                format_combo.setCurrentIndex(index)

        self.format_table.setCellWidget(row, 1, format_combo)

    def remove_format_row(self):
        """Supprime la ligne sélectionnée du tableau de formatage"""
        current_row = self.format_table.currentRow()
        if current_row >= 0:
            self.format_table.removeRow(current_row)

    def test_transformation(self):
        """Teste la transformation sur le fichier chargé"""
        if self.test_dataframe is None:
            QMessageBox.warning(self, "Attention", "Chargez d'abord un fichier exemple")
            return

        try:
            # Construire les règles de transformation
            rules = self.build_transformation_rules()

            # Appliquer la transformation
            transformed_df = self.file_processor.apply_transformation(
                self.test_dataframe.copy(),
                rules
            )

            # Afficher le résultat
            self.display_dataframe_preview_in_test(transformed_df)

            self.test_result_label.setText(
                f"✅ Transformation réussie! | "
                f"Lignes: {len(transformed_df)} | "
                f"Colonnes: {len(transformed_df.columns)}"
            )

        except Exception as e:
            logger.error(f"Erreur test transformation: {e}")
            self.test_result_label.setText(f"❌ Erreur: {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Erreur test transformation:\n{str(e)}")

    def display_dataframe_preview_in_test(self, df, max_rows: int = 20):
        """Affiche le résultat du test dans le tableau"""
        self.test_result_table.clear()

        preview_df = df.head(max_rows)

        self.test_result_table.setRowCount(len(preview_df))
        self.test_result_table.setColumnCount(len(preview_df.columns))
        self.test_result_table.setHorizontalHeaderLabels(list(preview_df.columns))

        for i, row in preview_df.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.test_result_table.setItem(i, j, item)

        self.test_result_table.resizeColumnsToContents()

    def build_transformation_rules(self) -> Dict:
        """Construit le dictionnaire de règles de transformation depuis l'UI"""
        rules = {}

        # Mapping
        column_mapping = {}
        for row in range(self.mapping_table.rowCount()):
            old_col = self.mapping_table.item(row, 0)
            new_col = self.mapping_table.item(row, 1)
            if old_col and new_col:
                old_col_text = old_col.text().strip()
                new_col_text = new_col.text().strip()
                if old_col_text and new_col_text:
                    column_mapping[old_col_text] = new_col_text
        if column_mapping:
            rules['column_mapping'] = column_mapping

        # Ajout de colonnes
        columns_to_add = {}
        for row in range(self.add_columns_table.rowCount()):
            col_name = self.add_columns_table.item(row, 0)
            value = self.add_columns_table.item(row, 1)
            if col_name and value:
                col_name_text = col_name.text().strip()
                value_text = value.text().strip()
                if col_name_text and value_text:
                    columns_to_add[col_name_text] = value_text
        if columns_to_add:
            rules['columns_to_add'] = columns_to_add

        # Suppression de colonnes
        columns_to_remove = []
        for row in range(self.remove_columns_table.rowCount()):
            col_name = self.remove_columns_table.item(row, 0)
            if col_name:
                col_name_text = col_name.text().strip()
                if col_name_text:
                    columns_to_remove.append(col_name_text)
        if columns_to_remove:
            rules['columns_to_remove'] = columns_to_remove

        # Formatage
        formatting = {}
        for row in range(self.format_table.rowCount()):
            col_name = self.format_table.item(row, 0)
            format_combo = self.format_table.cellWidget(row, 1)
            if col_name and format_combo:
                col_name_text = col_name.text().strip()
                format_type = format_combo.currentText()
                if col_name_text and format_type:
                    formatting[col_name_text] = format_type
        if formatting:
            rules['formatting'] = formatting

        return rules

    def save_transformation(self):
        """Sauvegarde la transformation dans le fichier de config"""
        if not self.current_supplier_id:
            QMessageBox.warning(self, "Attention", "Sélectionnez d'abord un fournisseur")
            return

        try:
            # Construire la transformation
            transformation_id = f"transform_{self.current_supplier_id}"
            rules = self.build_transformation_rules()

            transformation = {
                "id": transformation_id,
                "supplier_id": self.current_supplier_id,
                "description": f"Transformation pour {self.supplier_combo.currentText()}",
                **rules
            }

            # Charger le fichier existant ou créer nouveau
            config_path = Path(__file__).parent.parent.parent / "config" / "transformations.json"

            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {"transformations": []}

            # Remplacer ou ajouter la transformation
            found = False
            for i, trans in enumerate(config['transformations']):
                if trans.get('id') == transformation_id:
                    config['transformations'][i] = transformation
                    found = True
                    break

            if not found:
                config['transformations'].append(transformation)

            # Sauvegarder
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.transformation_saved.emit(self.current_supplier_id)

            QMessageBox.information(
                self,
                "Succès",
                f"Transformation sauvegardée avec succès!\n"
                f"ID: {transformation_id}"
            )

        except Exception as e:
            logger.error(f"Erreur sauvegarde transformation: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur sauvegarde:\n{str(e)}")
