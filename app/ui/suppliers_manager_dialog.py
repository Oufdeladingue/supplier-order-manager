"""
Interface de gestion des fournisseurs dans la base de données
Permet d'ajouter, modifier et supprimer des fournisseurs
"""

import sys
from pathlib import Path
from typing import Optional, Dict
from loguru import logger

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox,
    QLineEdit, QTextEdit, QDoubleSpinBox, QCheckBox, QComboBox,
    QFormLayout, QHeaderView
)
from PySide6.QtCore import Qt, Signal

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.supabase_client import supabase_client


class SupplierEditorDialog(QDialog):
    """Dialogue d'édition d'un fournisseur"""

    def __init__(self, supplier_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.supplier_data = supplier_data
        self.is_new = supplier_data is None

        self.init_ui()

        if supplier_data:
            self.load_supplier_data()

    def init_ui(self):
        """Initialise l'interface"""
        title = "Nouveau Fournisseur" if self.is_new else "Modifier Fournisseur"
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 600, 700)

        layout = QVBoxLayout(self)

        # Formulaire
        form_layout = QFormLayout()

        # Code fournisseur
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("ex: honda")
        form_layout.addRow("Code*:", self.code_input)

        # Nom
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ex: Honda")
        form_layout.addRow("Nom*:", self.name_input)

        # Source
        self.source_combo = QComboBox()
        self.source_combo.addItems(["ftp", "email", "manual"])
        form_layout.addRow("Source*:", self.source_combo)

        # Chemin FTP
        self.ftp_path_input = QLineEdit()
        self.ftp_path_input.setPlaceholderText("/home/user/fournisseurs")
        form_layout.addRow("Chemin FTP:", self.ftp_path_input)

        # Patterns de fichiers
        self.patterns_input = QTextEdit()
        self.patterns_input.setPlaceholderText('Honda-*.csv\nHonda_*.xlsx')
        self.patterns_input.setMaximumHeight(80)
        form_layout.addRow("Patterns fichiers*:", self.patterns_input)

        # Pattern email
        self.email_pattern_input = QLineEdit()
        self.email_pattern_input.setPlaceholderText("commandes@fournisseur.com")
        form_layout.addRow("Email:", self.email_pattern_input)

        # ID transformation
        self.transform_id_input = QLineEdit()
        self.transform_id_input.setPlaceholderText("transform_honda")
        form_layout.addRow("ID Transformation:", self.transform_id_input)

        # Minimum de commande
        self.min_order_input = QDoubleSpinBox()
        self.min_order_input.setRange(0, 999999)
        self.min_order_input.setSuffix(" €")
        self.min_order_input.setValue(0)
        form_layout.addRow("Minimum commande:", self.min_order_input)

        # URL Logo
        self.logo_url_input = QLineEdit()
        self.logo_url_input.setPlaceholderText("https://example.com/logo.png")
        form_layout.addRow("URL Logo:", self.logo_url_input)

        # Actif
        self.active_checkbox = QCheckBox("Fournisseur actif")
        self.active_checkbox.setChecked(True)
        form_layout.addRow("Status:", self.active_checkbox)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes et commentaires...")
        self.notes_input.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_input)

        layout.addLayout(form_layout)

        # Aide
        help_label = QLabel(
            "<small><b>Patterns de fichiers:</b> Un pattern par ligne (ex: Honda-*.csv)<br>"
            "<b>Code:</b> Identifiant unique sans espaces ni accents</small>"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(help_label)

        # Boutons
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.clicked.connect(self.save_supplier)
        save_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def load_supplier_data(self):
        """Charge les données du fournisseur"""
        if not self.supplier_data:
            return

        self.code_input.setText(self.supplier_data.get('supplier_code', ''))
        self.code_input.setEnabled(False)  # Code non modifiable

        self.name_input.setText(self.supplier_data.get('name', ''))

        source = self.supplier_data.get('source', 'ftp')
        index = self.source_combo.findText(source)
        if index >= 0:
            self.source_combo.setCurrentIndex(index)

        self.ftp_path_input.setText(self.supplier_data.get('ftp_path', ''))

        # Patterns (JSON array)
        patterns = self.supplier_data.get('file_patterns', [])
        if patterns:
            self.patterns_input.setPlainText('\n'.join(patterns))

        self.email_pattern_input.setText(self.supplier_data.get('email_pattern', ''))
        self.transform_id_input.setText(self.supplier_data.get('transformation_id', ''))
        self.min_order_input.setValue(float(self.supplier_data.get('min_order_amount', 0)))
        self.logo_url_input.setText(self.supplier_data.get('logo_url', ''))
        self.active_checkbox.setChecked(self.supplier_data.get('active', True))
        self.notes_input.setPlainText(self.supplier_data.get('notes', ''))

    def save_supplier(self):
        """Sauvegarde le fournisseur"""
        # Validation
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        patterns_text = self.patterns_input.toPlainText().strip()

        if not code or not name:
            QMessageBox.warning(self, "Attention", "Le code et le nom sont obligatoires")
            return

        if not patterns_text:
            QMessageBox.warning(self, "Attention", "Au moins un pattern de fichier est requis")
            return

        # Préparer les patterns
        patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]

        # Préparer les données
        data = {
            'supplier_code': code,
            'name': name,
            'source': self.source_combo.currentText(),
            'ftp_path': self.ftp_path_input.text().strip() or None,
            'file_patterns': patterns,
            'email_pattern': self.email_pattern_input.text().strip() or None,
            'transformation_id': self.transform_id_input.text().strip() or None,
            'min_order_amount': self.min_order_input.value(),
            'logo_url': self.logo_url_input.text().strip() or None,
            'active': self.active_checkbox.isChecked(),
            'notes': self.notes_input.toPlainText().strip() or None
        }

        try:
            if self.is_new:
                # Créer
                result = supabase_client.client.table('suppliers').insert(data).execute()
            else:
                # Mettre à jour
                supplier_id = self.supplier_data['id']
                result = supabase_client.client.table('suppliers').update(data).eq('id', supplier_id).execute()

            if result.data:
                QMessageBox.information(self, "Succès", "Fournisseur sauvegardé avec succès!")
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", "Échec de la sauvegarde")

        except Exception as e:
            logger.error(f"Erreur sauvegarde fournisseur: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")


class SuppliersManagerDialog(QDialog):
    """
    Interface de gestion des fournisseurs
    """

    suppliers_updated = Signal()  # Signal émis quand la liste est modifiée

    def __init__(self, parent=None):
        super().__init__(parent)
        self.suppliers_data = []

        self.init_ui()
        self.load_suppliers()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Gestion des Fournisseurs")
        self.setGeometry(100, 100, 1200, 700)

        layout = QVBoxLayout(self)

        # En-tête
        header_layout = QHBoxLayout()

        title = QLabel("📦 Gestion des Fournisseurs")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.count_label = QLabel("0 fournisseur(s)")
        self.count_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self.count_label)

        layout.addLayout(header_layout)

        # Barre d'outils
        toolbar_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Nouveau Fournisseur")
        add_btn.clicked.connect(self.add_supplier)
        add_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        toolbar_layout.addWidget(add_btn)

        edit_btn = QPushButton("✏️ Modifier")
        edit_btn.clicked.connect(self.edit_supplier)
        toolbar_layout.addWidget(edit_btn)
        self.edit_btn = edit_btn

        delete_btn = QPushButton("🗑️ Supprimer")
        delete_btn.clicked.connect(self.delete_supplier)
        toolbar_layout.addWidget(delete_btn)
        self.delete_btn = delete_btn

        toolbar_layout.addStretch()

        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.load_suppliers)
        toolbar_layout.addWidget(refresh_btn)

        layout.addLayout(toolbar_layout)

        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Code", "Nom", "Source", "Patterns", "Min Commande", "Actif", "Modifié", "ID"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(7, True)  # ID caché

        # Largeurs colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(lambda: self.edit_supplier())

        layout.addWidget(self.table)

        # Info
        info_label = QLabel(
            "💡 Double-cliquez sur une ligne pour modifier | "
            "Les modifications sont synchronisées entre tous les utilisateurs"
        )
        info_label.setStyleSheet("color: #666; padding: 5px; font-size: 11px;")
        layout.addWidget(info_label)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # Désactiver boutons par défaut
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def load_suppliers(self):
        """Charge les fournisseurs depuis Supabase"""
        try:
            response = supabase_client.client.table('suppliers').select('*').order('name').execute()

            self.suppliers_data = response.data

            # Afficher dans le tableau
            self.table.setRowCount(len(self.suppliers_data))

            for i, supplier in enumerate(self.suppliers_data):
                # Code
                self.table.setItem(i, 0, QTableWidgetItem(supplier.get('supplier_code', '')))

                # Nom
                self.table.setItem(i, 1, QTableWidgetItem(supplier.get('name', '')))

                # Source
                self.table.setItem(i, 2, QTableWidgetItem(supplier.get('source', '')))

                # Patterns
                patterns = supplier.get('file_patterns', [])
                patterns_str = ', '.join(patterns[:2])  # 2 premiers
                if len(patterns) > 2:
                    patterns_str += f' +{len(patterns)-2}'
                self.table.setItem(i, 3, QTableWidgetItem(patterns_str))

                # Min commande
                min_order = supplier.get('min_order_amount', 0)
                self.table.setItem(i, 4, QTableWidgetItem(f"{min_order:.0f} €"))

                # Actif
                active = "✓" if supplier.get('active', False) else "✗"
                active_item = QTableWidgetItem(active)
                if supplier.get('active', False):
                    active_item.setForeground(Qt.darkGreen)
                else:
                    active_item.setForeground(Qt.red)
                self.table.setItem(i, 5, active_item)

                # Modifié
                updated = supplier.get('updated_at', '')
                if updated:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    updated_str = dt.strftime('%d/%m/%Y')
                else:
                    updated_str = '-'
                self.table.setItem(i, 6, QTableWidgetItem(updated_str))

                # ID (caché)
                self.table.setItem(i, 7, QTableWidgetItem(supplier.get('id', '')))

            self.count_label.setText(f"{len(self.suppliers_data)} fournisseur(s)")

            logger.info(f"{len(self.suppliers_data)} fournisseur(s) chargé(s)")

        except Exception as e:
            logger.error(f"Erreur chargement fournisseurs: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement:\n{str(e)}")

    def on_selection_changed(self):
        """Appelé quand la sélection change"""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def add_supplier(self):
        """Ajoute un nouveau fournisseur"""
        dialog = SupplierEditorDialog(parent=self)

        if dialog.exec() == QDialog.Accepted:
            self.load_suppliers()
            self.suppliers_updated.emit()

    def edit_supplier(self):
        """Modifie le fournisseur sélectionné"""
        selected_rows = self.table.selectedItems()

        if not selected_rows:
            return

        row = selected_rows[0].row()
        supplier_id = self.table.item(row, 7).text()

        # Trouver les données complètes
        supplier_data = next((s for s in self.suppliers_data if s['id'] == supplier_id), None)

        if not supplier_data:
            QMessageBox.warning(self, "Erreur", "Fournisseur introuvable")
            return

        dialog = SupplierEditorDialog(supplier_data, parent=self)

        if dialog.exec() == QDialog.Accepted:
            self.load_suppliers()
            self.suppliers_updated.emit()

    def delete_supplier(self):
        """Supprime le fournisseur sélectionné"""
        selected_rows = self.table.selectedItems()

        if not selected_rows:
            return

        row = selected_rows[0].row()
        supplier_id = self.table.item(row, 7).text()
        supplier_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer le fournisseur:\n\n{supplier_name}\n\n"
            "Cette action est irréversible!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            result = supabase_client.client.table('suppliers').delete().eq('id', supplier_id).execute()

            if result.data or not result.data:  # Supabase retourne [] en cas de succès parfois
                QMessageBox.information(self, "Succès", "Fournisseur supprimé")
                self.load_suppliers()
                self.suppliers_updated.emit()
            else:
                QMessageBox.critical(self, "Erreur", "Échec de la suppression")

        except Exception as e:
            logger.error(f"Erreur suppression fournisseur: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
