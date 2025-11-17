"""
Interface de gestion des fournisseurs dans la base de données
Version 2 - avec onglets et informations étendues
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict
from loguru import logger

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QMessageBox, QGroupBox,
    QLineEdit, QTextEdit, QDoubleSpinBox, QCheckBox, QComboBox,
    QFormLayout, QHeaderView, QTabWidget, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.supabase_client import supabase_client


class SupplierEditorDialog(QDialog):
    """Dialogue d'édition d'un fournisseur avec onglets"""

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
        self.setMinimumSize(750, 600)  # Taille minimale
        self.resize(750, 650)  # Taille par défaut plus petite

        layout = QVBoxLayout(self)

        # Onglets
        self.tabs = QTabWidget()

        # Onglet 1: Informations générales
        tab_general = self.create_general_tab()
        self.tabs.addTab(tab_general, "📋 Informations générales")

        # Onglet 2: Paramètres d'import
        tab_import = self.create_import_tab()
        self.tabs.addTab(tab_import, "⚙️ Import")

        # Onglet 3: Paramètres d'impression
        tab_print = self.create_print_tab()
        self.tabs.addTab(tab_print, "🖨️ Impressions")

        # Onglet 4: Paramètres d'affichage
        tab_display = self.create_display_tab()
        self.tabs.addTab(tab_display, "👁️ Affichage")

        # Onglet 5: Connexion Web automatique
        tab_web = self.create_web_tab()
        self.tabs.addTab(tab_web, "🌐 Web")

        layout.addWidget(self.tabs)

        # Boutons
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.clicked.connect(self.save_supplier)
        save_btn.setStyleSheet("padding: 10px; font-weight: bold; background-color: #4CAF50; color: white;")
        buttons_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("padding: 10px;")
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def create_general_tab(self) -> QWidget:
        """Crée l'onglet des informations générales"""
        # Créer le widget de contenu
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        form_layout = QFormLayout()

        # === Informations de base ===
        group_base = QGroupBox("Informations de base")
        base_layout = QFormLayout()

        # Nom
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ex: Honda")
        base_layout.addRow("Nom*:", self.name_input)

        # Slug de filtre
        self.slug_input = QLineEdit()
        self.slug_input.setPlaceholderText("ex: Honda")
        slug_help = QLabel("<small>Premières lettres du fichier pour filtrer (ex: 'Honda' pour 'Honda-13-11-25.csv')</small>")
        slug_help.setWordWrap(True)
        base_layout.addRow("Slug de filtre*:", self.slug_input)
        base_layout.addRow("", slug_help)

        # Logo - Sélecteur depuis Supabase Storage
        logo_layout = QHBoxLayout()

        self.logo_combo = QComboBox()
        self.logo_combo.setEditable(False)
        self.logo_combo.addItem("(Aucun logo)", "")
        logo_layout.addWidget(self.logo_combo, 1)

        # Bouton pour rafraîchir la liste des logos
        refresh_logos_btn = QPushButton("🔄")
        refresh_logos_btn.setMaximumWidth(40)
        refresh_logos_btn.setToolTip("Rafraîchir la liste des logos")
        refresh_logos_btn.clicked.connect(self.load_logos_from_storage)
        logo_layout.addWidget(refresh_logos_btn)

        base_layout.addRow("Logo:", logo_layout)

        # Charger les logos au démarrage
        self.load_logos_from_storage()

        # Actif
        self.active_checkbox = QCheckBox("Fournisseur actif")
        self.active_checkbox.setChecked(True)
        base_layout.addRow("Status:", self.active_checkbox)

        group_base.setLayout(base_layout)
        layout.addWidget(group_base)

        # === Coordonnées ===
        group_contact = QGroupBox("Coordonnées")
        contact_layout = QFormLayout()

        # Téléphone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("01 23 45 67 89")
        contact_layout.addRow("Téléphone:", self.phone_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("contact@fournisseur.com")
        contact_layout.addRow("Email:", self.email_input)

        # Site web
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("https://www.fournisseur.com")
        contact_layout.addRow("Site web:", self.website_input)

        group_contact.setLayout(contact_layout)
        layout.addWidget(group_contact)

        # === Accès web ===
        group_web = QGroupBox("Accès espace client web")
        web_layout = QFormLayout()

        # User web
        self.web_user_input = QLineEdit()
        self.web_user_input.setPlaceholderText("mon_compte")
        web_layout.addRow("Identifiant:", self.web_user_input)

        # Mot de passe web
        self.web_password_input = QLineEdit()
        self.web_password_input.setPlaceholderText("••••••••")
        self.web_password_input.setEchoMode(QLineEdit.Password)
        web_layout.addRow("Mot de passe:", self.web_password_input)

        show_pwd_btn = QCheckBox("Afficher le mot de passe")
        show_pwd_btn.toggled.connect(
            lambda checked: self.web_password_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )
        web_layout.addRow("", show_pwd_btn)

        group_web.setLayout(web_layout)
        layout.addWidget(group_web)

        # === Patterns de fichiers ===
        group_patterns = QGroupBox("Patterns de fichiers")
        group_patterns.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        patterns_layout = QVBoxLayout()

        # Description
        patterns_help = QLabel(
            "📋 <b>Définissez les patterns de fichiers à récupérer pour ce fournisseur</b><br>"
            "<small>• Utilisez les wildcards: * (n'importe quels caractères) ou ? (un caractère)</small><br>"
            "<small>• Un pattern par ligne pour gérer plusieurs types de fichiers</small><br>"
            "<small>• Exemples: <code>Honda-*.csv</code>, <code>order_??.xlsx</code>, <code>data_*.csv</code></small>"
        )
        patterns_help.setWordWrap(True)
        patterns_help.setStyleSheet("padding: 5px; background-color: #FFF3E0; border-radius: 3px;")
        patterns_layout.addWidget(patterns_help)

        # Champ patterns (multi-lignes)
        patterns_label = QLabel("Patterns (un par ligne)*:")
        patterns_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        patterns_layout.addWidget(patterns_label)

        self.patterns_input = QTextEdit()
        self.patterns_input.setPlaceholderText(
            'Honda-*.csv\n'
            'Honda_commande_*.xlsx\n'
            'ORDER-*.csv'
        )
        self.patterns_input.setMaximumHeight(80)
        self.patterns_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 5px;
                border: 2px solid #FF9800;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border-color: #F57C00;
            }
        """)
        patterns_layout.addWidget(self.patterns_input)

        group_patterns.setLayout(patterns_layout)
        layout.addWidget(group_patterns)

        layout.addStretch()

        # Créer le scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return scroll_area

    def create_import_tab(self) -> QWidget:
        """Crée l'onglet des paramètres d'import"""
        # Créer le widget de contenu
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # === Format de sortie ===
        group_format = QGroupBox("Format de sortie")
        format_layout = QFormLayout()

        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["xlsx", "csv"])
        format_layout.addRow("Format:", self.output_format_combo)

        format_help = QLabel("<small>Format du fichier généré après transformation</small>")
        format_help.setWordWrap(True)
        format_layout.addRow("", format_help)

        group_format.setLayout(format_layout)
        layout.addWidget(group_format)

        # === En-tête du fichier source ===
        group_source = QGroupBox("Fichier source")
        source_layout = QVBoxLayout()

        self.has_header_checkbox = QCheckBox("Le fichier source contient une ligne d'en-tête")
        self.has_header_checkbox.setChecked(False)
        source_layout.addWidget(self.has_header_checkbox)

        header_help = QLabel("<small>Cochez si la première ligne du fichier CSV contient les noms de colonnes</small>")
        header_help.setWordWrap(True)
        source_layout.addWidget(header_help)

        # Zéros significatifs
        self.leading_zeros_checkbox = QCheckBox("Conserver les zéros significatifs")
        self.leading_zeros_checkbox.setChecked(False)
        source_layout.addWidget(self.leading_zeros_checkbox)

        zeros_help = QLabel("<small>Préserver les zéros en début de valeur (ex: '00123' reste '00123')</small>")
        zeros_help.setWordWrap(True)
        source_layout.addWidget(zeros_help)

        group_source.setLayout(source_layout)
        layout.addWidget(group_source)

        # === Ajout d'en-tête au fichier généré ===
        group_output_header = QGroupBox("En-tête du fichier généré")
        output_header_layout = QVBoxLayout()

        self.add_output_header_checkbox = QCheckBox("Ajouter une ligne d'en-tête au fichier généré")
        output_header_layout.addWidget(self.add_output_header_checkbox)

        # Type d'en-tête
        header_type_layout = QHBoxLayout()
        self.header_type_combo = QComboBox()
        self.header_type_combo.addItems(["Texte fixe", "Texte + date du jour"])
        self.header_type_combo.setEnabled(False)
        header_type_layout.addWidget(QLabel("Type:"))
        header_type_layout.addWidget(self.header_type_combo)
        header_type_layout.addStretch()
        output_header_layout.addLayout(header_type_layout)

        # Contenu de l'en-tête
        self.header_content_input = QLineEdit()
        self.header_content_input.setPlaceholderText("Ref;Quantité;Désignation;Prix;Client;EAN13;N° commande")
        self.header_content_input.setEnabled(False)
        output_header_layout.addWidget(QLabel("Contenu de l'en-tête:"))
        output_header_layout.addWidget(self.header_content_input)

        header_content_help = QLabel(
            "<small>• <b>Texte fixe:</b> Le texte sera inséré tel quel<br>"
            "• <b>Texte + date:</b> La date du jour sera ajoutée à la fin (ex: 'Commande du 15/01/2025')</small>"
        )
        header_content_help.setWordWrap(True)
        output_header_layout.addWidget(header_content_help)

        group_output_header.setLayout(output_header_layout)
        layout.addWidget(group_output_header)

        # === Exception sur les doublons ===
        group_duplicates = QGroupBox("Exception sur les doublons")
        duplicates_layout = QVBoxLayout()

        self.check_duplicates_checkbox = QCheckBox("Fusionner les références en doublon en additionnant les quantités")
        duplicates_layout.addWidget(self.check_duplicates_checkbox)

        duplicates_help = QLabel(
            "<small>• Si coché: Les lignes avec la même référence seront fusionnées<br>"
            "• Les quantités seront additionnées (ex: 2 lignes avec ref 13175, qté 1 et 2 → 1 ligne ref 13175, qté 3)<br>"
            "• Seule la première colonne (références) sera vérifiée</small>"
        )
        duplicates_help.setWordWrap(True)
        duplicates_layout.addWidget(duplicates_help)

        group_duplicates.setLayout(duplicates_layout)
        layout.addWidget(group_duplicates)

        # === Suppression de colonnes ===
        group_remove_cols = QGroupBox("Suppression de colonnes")
        remove_cols_layout = QVBoxLayout()

        remove_cols_help = QLabel(
            "📋 <b>Colonnes à supprimer du fichier généré</b><br>"
            "<small>Cochez les colonnes à ne pas inclure dans le fichier de sortie</small>"
        )
        remove_cols_help.setWordWrap(True)
        remove_cols_layout.addWidget(remove_cols_help)

        # Cases à cocher pour chaque colonne (comme dans l'onglet Impressions)
        checkboxes_layout = QHBoxLayout()

        self.import_col_ref_checkbox = QCheckBox("Ref")
        self.import_col_qty_checkbox = QCheckBox("Qté")
        self.import_col_designation_checkbox = QCheckBox("Désignation")
        self.import_col_price_checkbox = QCheckBox("Prix")
        self.import_col_client_checkbox = QCheckBox("Client")
        self.import_col_ean13_checkbox = QCheckBox("EAN13")
        self.import_col_order_checkbox = QCheckBox("N° cde")

        checkboxes_layout.addWidget(self.import_col_ref_checkbox)
        checkboxes_layout.addWidget(self.import_col_qty_checkbox)
        checkboxes_layout.addWidget(self.import_col_designation_checkbox)
        checkboxes_layout.addWidget(self.import_col_price_checkbox)
        checkboxes_layout.addWidget(self.import_col_client_checkbox)
        checkboxes_layout.addWidget(self.import_col_ean13_checkbox)
        checkboxes_layout.addWidget(self.import_col_order_checkbox)
        checkboxes_layout.addStretch()

        remove_cols_layout.addLayout(checkboxes_layout)

        group_remove_cols.setLayout(remove_cols_layout)
        layout.addWidget(group_remove_cols)

        # === Suppression de préfixes ===
        group_import_prefix = QGroupBox("Suppression de préfixes")
        group_import_prefix.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF5722;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        import_prefix_layout = QVBoxLayout()

        # Description
        import_prefix_help = QLabel(
            "✂️ <b>Définissez les préfixes à supprimer de la colonne Ref</b><br>"
            "<small>• Un préfixe par ligne (max 8 caractères par préfixe)</small><br>"
            "<small>• Les préfixes seront retirés du début de chaque référence</small><br>"
            "<small>• Exemple: <code>HOP</code> transforme <code>HOP17512</code> en <code>17512</code></small>"
        )
        import_prefix_help.setWordWrap(True)
        import_prefix_help.setStyleSheet("padding: 5px; background-color: #FFE0B2; border-radius: 3px;")
        import_prefix_layout.addWidget(import_prefix_help)

        # Champ préfixes (multi-lignes)
        import_prefix_label = QLabel("Préfixes (un par ligne, max 8 car. chacun):")
        import_prefix_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        import_prefix_layout.addWidget(import_prefix_label)

        self.import_prefix_input = QTextEdit()
        self.import_prefix_input.setPlaceholderText(
            'HOP\n'
            'ACME-\n'
            'SUP'
        )
        self.import_prefix_input.setMaximumHeight(70)
        self.import_prefix_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 5px;
                border: 2px solid #FF5722;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border-color: #E64A19;
            }
        """)
        import_prefix_layout.addWidget(self.import_prefix_input)

        group_import_prefix.setLayout(import_prefix_layout)
        layout.addWidget(group_import_prefix)

        # === Nom du fichier de sortie ===
        group_filename = QGroupBox("Nom du fichier de sortie")
        filename_layout = QVBoxLayout()

        filename_help = QLabel(
            "📝 <b>Nom du fichier généré</b><br>"
            "<small>Variables disponibles: {supplier} = slug du fournisseur, {date} = date du jour, {time} = heure (HHMMSS)</small>"
        )
        filename_help.setWordWrap(True)
        filename_layout.addWidget(filename_help)

        # Format de date
        date_format_layout = QHBoxLayout()
        date_format_layout.addWidget(QLabel("Format de date:"))

        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems([
            "jj-mm-aa (15-01-25)",
            "jj-mm-aaaa (15-01-2025)",
            "aaaa-mm-jj (2025-01-15)",
            "aaaammjj (20250115)",
            "jjmmaa (150125)",
            "jjmmaaaa (15012025)"
        ])
        self.date_format_combo.currentTextChanged.connect(self.update_filename_example)
        date_format_layout.addWidget(self.date_format_combo)
        date_format_layout.addStretch()
        filename_layout.addLayout(date_format_layout)

        # Modèle de nom de fichier
        filename_layout.addWidget(QLabel("Modèle de nom:"))
        self.output_filename_input = QLineEdit()
        self.output_filename_input.setPlaceholderText("{supplier}_{date}")
        self.output_filename_input.setText("{supplier}_{date}")
        self.output_filename_input.textChanged.connect(self.update_filename_example)
        filename_layout.addWidget(self.output_filename_input)

        # Exemple
        self.filename_example = QLabel("<small><i>Exemple: honda_15-01-25.xlsx</i></small>")
        filename_layout.addWidget(self.filename_example)

        group_filename.setLayout(filename_layout)
        layout.addWidget(group_filename)

        # Connecter les changements
        self.add_output_header_checkbox.toggled.connect(self.toggle_header_fields)

        layout.addStretch()

        # Créer le scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return scroll_area

    def create_print_tab(self) -> QWidget:
        """Crée l'onglet des paramètres d'impression"""
        # Créer le widget de contenu
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # === Suppression de colonnes ===
        group_columns = QGroupBox("Suppression de colonnes")
        columns_layout = QVBoxLayout()

        columns_help = QLabel("<small>Cochez les colonnes à supprimer du document d'impression</small>")
        columns_help.setWordWrap(True)
        columns_layout.addWidget(columns_help)

        # Layout horizontal pour les cases à cocher
        checkboxes_layout = QHBoxLayout()

        # Créer les checkboxes pour chaque colonne
        self.col_ref_checkbox = QCheckBox("Ref")
        self.col_qty_checkbox = QCheckBox("Qté")
        self.col_designation_checkbox = QCheckBox("Désignation")
        self.col_price_checkbox = QCheckBox("Prix")
        self.col_client_checkbox = QCheckBox("Client")
        self.col_ean13_checkbox = QCheckBox("EAN13")
        self.col_order_checkbox = QCheckBox("N° cde")

        checkboxes_layout.addWidget(self.col_ref_checkbox)
        checkboxes_layout.addWidget(self.col_qty_checkbox)
        checkboxes_layout.addWidget(self.col_designation_checkbox)
        checkboxes_layout.addWidget(self.col_price_checkbox)
        checkboxes_layout.addWidget(self.col_client_checkbox)
        checkboxes_layout.addWidget(self.col_ean13_checkbox)
        checkboxes_layout.addWidget(self.col_order_checkbox)
        checkboxes_layout.addStretch()

        columns_layout.addLayout(checkboxes_layout)
        group_columns.setLayout(columns_layout)
        layout.addWidget(group_columns)

        # === Suppression de préfixe ===
        group_prefix = QGroupBox("Suppression de préfixes")
        group_prefix.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9C27B0;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        prefix_layout = QVBoxLayout()

        # Description
        prefix_help = QLabel(
            "✂️ <b>Définissez les préfixes à supprimer de la colonne Ref</b><br>"
            "<small>• Un préfixe par ligne (max 8 caractères par préfixe)</small><br>"
            "<small>• Les préfixes seront retirés du début de chaque référence</small><br>"
            "<small>• Exemple: <code>HOP</code> transforme <code>HOP17512</code> en <code>17512</code></small>"
        )
        prefix_help.setWordWrap(True)
        prefix_help.setStyleSheet("padding: 5px; background-color: #F3E5F5; border-radius: 3px;")
        prefix_layout.addWidget(prefix_help)

        # Champ préfixes (multi-lignes)
        prefix_label = QLabel("Préfixes (un par ligne, max 8 car. chacun):")
        prefix_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        prefix_layout.addWidget(prefix_label)

        self.prefix_input = QTextEdit()
        self.prefix_input.setPlaceholderText(
            'HOP\n'
            'ACME-\n'
            'SUP'
        )
        self.prefix_input.setMaximumHeight(70)
        self.prefix_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 5px;
                border: 2px solid #9C27B0;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border-color: #7B1FA2;
            }
        """)
        prefix_layout.addWidget(self.prefix_input)

        group_prefix.setLayout(prefix_layout)
        layout.addWidget(group_prefix)

        # === Date en fin de page ===
        group_date = QGroupBox("Date en fin de page")
        date_layout = QVBoxLayout()

        self.add_date_checkbox = QCheckBox("Ajouter la date du jour")
        date_layout.addWidget(self.add_date_checkbox)

        date_help = QLabel("<small>Insère la date du jour dans la colonne C (3) de la deuxième ligne non vide</small>")
        date_help.setWordWrap(True)
        date_layout.addWidget(date_help)

        group_date.setLayout(date_layout)
        layout.addWidget(group_date)

        # === Séparation des fichiers ===
        group_split = QGroupBox("Fusion des fichiers")
        split_layout = QVBoxLayout()

        self.split_files_checkbox = QCheckBox("Séparer les fichiers avec une ligne vide")
        split_layout.addWidget(self.split_files_checkbox)

        split_help = QLabel(
            "<small>• <b>Coché :</b> Chaque fichier sera traité individuellement puis juxtaposé avec une ligne vide entre chaque</small><br>"
            "<small>• <b>Décoché :</b> Tous les fichiers seront fusionnés et triés globalement par référence (colonne A)</small>"
        )
        split_help.setWordWrap(True)
        split_layout.addWidget(split_help)

        group_split.setLayout(split_layout)
        layout.addWidget(group_split)

        # === Format de sortie ===
        group_format = QGroupBox("Format de sortie")
        format_layout = QFormLayout()

        self.print_format_combo = QComboBox()
        self.print_format_combo.addItems(["A4", "A3", "Letter"])
        format_layout.addRow("Format papier:", self.print_format_combo)

        format_help = QLabel("<small>Format de page pour l'impression (par défaut: A4)</small>")
        format_help.setWordWrap(True)
        format_layout.addRow("", format_help)

        group_format.setLayout(format_layout)
        layout.addWidget(group_format)

        # === Aperçu des paramètres ===
        group_preview = QGroupBox("Aperçu de la configuration")
        preview_layout = QVBoxLayout()

        self.print_preview_label = QLabel()
        self.print_preview_label.setWordWrap(True)
        self.print_preview_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        preview_layout.addWidget(self.print_preview_label)

        group_preview.setLayout(preview_layout)
        layout.addWidget(group_preview)

        # Connecter les changements pour mettre à jour l'aperçu
        self.col_ref_checkbox.toggled.connect(self.update_print_preview)
        self.col_qty_checkbox.toggled.connect(self.update_print_preview)
        self.col_designation_checkbox.toggled.connect(self.update_print_preview)
        self.col_price_checkbox.toggled.connect(self.update_print_preview)
        self.col_client_checkbox.toggled.connect(self.update_print_preview)
        self.col_ean13_checkbox.toggled.connect(self.update_print_preview)
        self.col_order_checkbox.toggled.connect(self.update_print_preview)
        self.prefix_input.textChanged.connect(self.update_print_preview)
        self.add_date_checkbox.toggled.connect(self.update_print_preview)
        self.split_files_checkbox.toggled.connect(self.update_print_preview)
        self.print_format_combo.currentTextChanged.connect(self.update_print_preview)

        self.update_print_preview()

        layout.addStretch()

        # Créer le scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return scroll_area

    def create_display_tab(self) -> QWidget:
        """Crée l'onglet des paramètres d'affichage (pour le bouton Ouvrir)"""
        # Créer le widget de contenu
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # === Suppression de colonnes ===
        group_display_columns = QGroupBox("Suppression de colonnes")
        display_columns_layout = QVBoxLayout()

        columns_help = QLabel("<small>Cochez les colonnes à supprimer du fichier Excel ouvert</small>")
        columns_help.setWordWrap(True)
        display_columns_layout.addWidget(columns_help)

        # Layout horizontal pour les cases à cocher
        display_checkboxes_layout = QHBoxLayout()

        # Créer les checkboxes pour chaque colonne
        self.display_col_ref_checkbox = QCheckBox("Ref")
        self.display_col_qty_checkbox = QCheckBox("Qté")
        self.display_col_designation_checkbox = QCheckBox("Désignation")
        self.display_col_price_checkbox = QCheckBox("Prix")
        self.display_col_client_checkbox = QCheckBox("Client")
        self.display_col_ean13_checkbox = QCheckBox("EAN13")
        self.display_col_order_checkbox = QCheckBox("N° cde")

        display_checkboxes_layout.addWidget(self.display_col_ref_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_qty_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_designation_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_price_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_client_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_ean13_checkbox)
        display_checkboxes_layout.addWidget(self.display_col_order_checkbox)
        display_checkboxes_layout.addStretch()

        display_columns_layout.addLayout(display_checkboxes_layout)
        group_display_columns.setLayout(display_columns_layout)
        layout.addWidget(group_display_columns)

        # === Suppression de préfixes ===
        group_display_prefix = QGroupBox("Suppression de préfixes")
        group_display_prefix.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        display_prefix_layout = QVBoxLayout()

        # Description
        display_prefix_help = QLabel(
            "✂️ <b>Définissez les préfixes à supprimer de la colonne Ref</b><br>"
            "<small>• Un préfixe par ligne (max 8 caractères par préfixe)</small><br>"
            "<small>• Les préfixes seront retirés du début de chaque référence</small><br>"
            "<small>• Exemple: <code>HOP</code> transforme <code>HOP17512</code> en <code>17512</code></small>"
        )
        display_prefix_help.setWordWrap(True)
        display_prefix_help.setStyleSheet("padding: 5px; background-color: #E3F2FD; border-radius: 3px;")
        display_prefix_layout.addWidget(display_prefix_help)

        # Champ préfixes (multi-lignes)
        display_prefix_label = QLabel("Préfixes (un par ligne, max 8 car. chacun):")
        display_prefix_label.setStyleSheet("margin-top: 10px; font-weight: bold;")
        display_prefix_layout.addWidget(display_prefix_label)

        self.display_prefix_input = QTextEdit()
        self.display_prefix_input.setPlaceholderText(
            'HOP\n'
            'ACME-\n'
            'SUP'
        )
        self.display_prefix_input.setMaximumHeight(70)
        self.display_prefix_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                padding: 5px;
                border: 2px solid #2196F3;
                border-radius: 3px;
            }
            QTextEdit:focus {
                border-color: #1976D2;
            }
        """)
        display_prefix_layout.addWidget(self.display_prefix_input)

        group_display_prefix.setLayout(display_prefix_layout)
        layout.addWidget(group_display_prefix)

        # === Date en fin de page ===
        group_display_date = QGroupBox("Date en fin de page")
        display_date_layout = QVBoxLayout()

        self.display_add_date_checkbox = QCheckBox("Ajouter la date du jour")
        display_date_layout.addWidget(self.display_add_date_checkbox)

        display_date_help = QLabel("<small>Insère la date du jour dans la colonne C (3) à la dernière ligne du fichier</small>")
        display_date_help.setWordWrap(True)
        display_date_layout.addWidget(display_date_help)

        group_display_date.setLayout(display_date_layout)
        layout.addWidget(group_display_date)

        # === Séparation des fichiers ===
        group_display_split = QGroupBox("Fusion des fichiers")
        display_split_layout = QVBoxLayout()

        self.display_split_files_checkbox = QCheckBox("Séparer les fichiers avec une ligne vide")
        display_split_layout.addWidget(self.display_split_files_checkbox)

        display_split_help = QLabel(
            "<small>• <b>Coché :</b> Chaque fichier sera traité individuellement puis juxtaposé avec une ligne vide entre chaque</small><br>"
            "<small>• <b>Décoché :</b> Tous les fichiers seront fusionnés et triés globalement par référence (colonne A)</small>"
        )
        display_split_help.setWordWrap(True)
        display_split_layout.addWidget(display_split_help)

        group_display_split.setLayout(display_split_layout)
        layout.addWidget(group_display_split)

        layout.addStretch()

        # Créer le scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return scroll_area

    def create_web_tab(self) -> QWidget:
        """Crée l'onglet de configuration de connexion Web automatique"""
        # Créer le widget de contenu
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # === URL de connexion ===
        group_url = QGroupBox("🌐 Page de connexion")
        url_layout = QFormLayout()

        self.web_url_input = QLineEdit()
        self.web_url_input.setPlaceholderText("https://www.example.com/login")
        url_layout.addRow("URL de la page de login:", self.web_url_input)

        group_url.setLayout(url_layout)
        layout.addWidget(group_url)

        # === Code client (optionnel) ===
        group_client_code = QGroupBox("🔑 Code client (optionnel)")
        client_code_layout = QVBoxLayout()

        self.web_client_code_enabled = QCheckBox("Activer le code client")
        self.web_client_code_enabled.stateChanged.connect(self.toggle_client_code_fields)
        client_code_layout.addWidget(self.web_client_code_enabled)

        client_code_form = QFormLayout()
        self.web_client_code_value = QLineEdit()
        self.web_client_code_value.setPlaceholderText("700085")
        self.web_client_code_value.setEnabled(False)
        client_code_form.addRow("Valeur:", self.web_client_code_value)

        self.web_client_code_selector = QLineEdit()
        self.web_client_code_selector.setPlaceholderText('input[placeholder="000000"]')
        self.web_client_code_selector.setEnabled(False)
        client_code_form.addRow("Sélecteur HTML:", self.web_client_code_selector)

        client_code_layout.addLayout(client_code_form)
        group_client_code.setLayout(client_code_layout)
        layout.addWidget(group_client_code)

        # === Login ===
        group_login = QGroupBox("👤 Identifiant de connexion")
        login_layout = QFormLayout()

        self.web_login_value = QLineEdit()
        self.web_login_value.setPlaceholderText("mon.email@example.com")
        login_layout.addRow("Login:", self.web_login_value)

        self.web_login_selector = QLineEdit()
        self.web_login_selector.setPlaceholderText('input[type="email"]')
        login_layout.addRow("Sélecteur HTML:", self.web_login_selector)

        group_login.setLayout(login_layout)
        layout.addWidget(group_login)

        # === Mot de passe ===
        group_password = QGroupBox("🔒 Mot de passe")
        password_layout = QFormLayout()

        self.web_password_value = QLineEdit()
        self.web_password_value.setPlaceholderText("Mj@rdin2026")
        self.web_password_value.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Mot de passe:", self.web_password_value)

        self.web_password_selector = QLineEdit()
        self.web_password_selector.setPlaceholderText('input[type="password"]')
        password_layout.addRow("Sélecteur HTML:", self.web_password_selector)

        group_password.setLayout(password_layout)
        layout.addWidget(group_password)

        # === Autre champ (optionnel) ===
        group_other = QGroupBox("➕ Autre champ (optionnel)")
        other_layout = QVBoxLayout()

        self.web_other_enabled = QCheckBox("Activer un autre champ")
        self.web_other_enabled.stateChanged.connect(self.toggle_other_field)
        other_layout.addWidget(self.web_other_enabled)

        other_form = QFormLayout()
        self.web_other_value = QLineEdit()
        self.web_other_value.setPlaceholderText("Valeur supplémentaire")
        self.web_other_value.setEnabled(False)
        other_form.addRow("Valeur:", self.web_other_value)

        self.web_other_selector = QLineEdit()
        self.web_other_selector.setPlaceholderText('input[name="other_field"]')
        self.web_other_selector.setEnabled(False)
        other_form.addRow("Sélecteur HTML:", self.web_other_selector)

        other_layout.addLayout(other_form)
        group_other.setLayout(other_layout)
        layout.addWidget(group_other)

        # === Bouton de validation ===
        group_submit = QGroupBox("✅ Bouton de validation")
        submit_layout = QFormLayout()

        self.web_submit_selector = QLineEdit()
        self.web_submit_selector.setPlaceholderText('//button[normalize-space(text())="Se connecter"]')
        submit_layout.addRow("Sélecteur du bouton:", self.web_submit_selector)

        group_submit.setLayout(submit_layout)
        layout.addWidget(group_submit)

        # === Validation intermédiaire (optionnel) ===
        group_intermediate = QGroupBox("⏭️ Validation intermédiaire (optionnel)")
        intermediate_layout = QVBoxLayout()

        self.web_intermediate_enabled = QCheckBox("Activer validation intermédiaire")
        self.web_intermediate_enabled.stateChanged.connect(self.toggle_intermediate_validation)
        intermediate_layout.addWidget(self.web_intermediate_enabled)

        intermediate_form = QFormLayout()
        self.web_intermediate_selector = QLineEdit()
        self.web_intermediate_selector.setPlaceholderText('//button[normalize-space(text())="Valider"]')
        self.web_intermediate_selector.setEnabled(False)
        intermediate_form.addRow("Sélecteur:", self.web_intermediate_selector)

        intermediate_layout.addLayout(intermediate_form)
        group_intermediate.setLayout(intermediate_layout)
        layout.addWidget(group_intermediate)

        # === Cookie (optionnel) ===
        group_cookie = QGroupBox("🍪 Bannière cookies (optionnel)")
        cookie_layout = QVBoxLayout()

        self.web_cookie_enabled = QCheckBox("Activer gestion des cookies")
        self.web_cookie_enabled.stateChanged.connect(self.toggle_cookie_banner)
        cookie_layout.addWidget(self.web_cookie_enabled)

        cookie_form = QFormLayout()
        self.web_cookie_selector = QLineEdit()
        self.web_cookie_selector.setPlaceholderText('button[id="accept-cookies"]')
        self.web_cookie_selector.setEnabled(False)
        cookie_form.addRow("Sélecteur:", self.web_cookie_selector)

        cookie_layout.addLayout(cookie_form)
        group_cookie.setLayout(cookie_layout)
        layout.addWidget(group_cookie)

        # === Détection Captcha ===
        group_captcha = QGroupBox("🤖 Détection Captcha")
        captcha_layout = QVBoxLayout()

        self.web_captcha_detect = QCheckBox("Le site utilise un captcha")
        captcha_help = QLabel("<small>Si coché, l'automatisation attendra une intervention manuelle pour le captcha</small>")
        captcha_help.setWordWrap(True)
        captcha_layout.addWidget(self.web_captcha_detect)
        captcha_layout.addWidget(captcha_help)

        group_captcha.setLayout(captcha_layout)
        layout.addWidget(group_captcha)

        layout.addStretch()

        # Créer le scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        return scroll_area

    def toggle_client_code_fields(self, state):
        """Active/désactive les champs de code client"""
        # Utiliser bool(state) car state est un int: 0=unchecked, 2=checked
        enabled = bool(state)
        self.web_client_code_value.setEnabled(enabled)
        self.web_client_code_selector.setEnabled(enabled)

    def toggle_other_field(self, state):
        """Active/désactive l'autre champ"""
        # Utiliser bool(state) car state est un int: 0=unchecked, 2=checked
        enabled = bool(state)
        self.web_other_value.setEnabled(enabled)
        self.web_other_selector.setEnabled(enabled)

    def toggle_intermediate_validation(self, state):
        """Active/désactive la validation intermédiaire"""
        # Utiliser bool(state) car state est un int: 0=unchecked, 2=checked
        enabled = bool(state)
        self.web_intermediate_selector.setEnabled(enabled)

    def toggle_cookie_banner(self, state):
        """Active/désactive la gestion des cookies"""
        # Utiliser bool(state) car state est un int: 0=unchecked, 2=checked
        enabled = bool(state)
        self.web_cookie_selector.setEnabled(enabled)

    def update_print_preview(self):
        """Met à jour l'aperçu de la configuration d'impression"""
        # Collecter les colonnes à supprimer
        columns_to_remove = []
        if self.col_ref_checkbox.isChecked():
            columns_to_remove.append("Ref")
        if self.col_qty_checkbox.isChecked():
            columns_to_remove.append("Qté")
        if self.col_designation_checkbox.isChecked():
            columns_to_remove.append("Désignation")
        if self.col_price_checkbox.isChecked():
            columns_to_remove.append("Prix")
        if self.col_client_checkbox.isChecked():
            columns_to_remove.append("Client")
        if self.col_ean13_checkbox.isChecked():
            columns_to_remove.append("EAN13")
        if self.col_order_checkbox.isChecked():
            columns_to_remove.append("N° cde")

        # Récupérer les préfixes (un par ligne)
        prefixes_text = self.prefix_input.toPlainText().strip()
        prefixes = [p.strip() for p in prefixes_text.split('\n') if p.strip()]

        add_date = self.add_date_checkbox.isChecked()
        paper_format = self.print_format_combo.currentText()

        # Construire le texte d'aperçu
        preview_text = "<b>Configuration d'impression :</b><br><br>"

        if columns_to_remove:
            preview_text += f"• Colonnes supprimées : <b>{', '.join(columns_to_remove)}</b><br>"
        else:
            preview_text += "• Aucune colonne supprimée<br>"

        if prefixes:
            if len(prefixes) == 1:
                preview_text += f"• Préfixe à supprimer : <b>{prefixes[0]}</b><br>"
            else:
                preview_text += f"• Préfixes à supprimer : <b>{', '.join(prefixes)}</b><br>"
        else:
            preview_text += "• Aucun préfixe à supprimer<br>"

        preview_text += f"• Date en fin de page : <b>{'Oui' if add_date else 'Non'}</b><br>"
        preview_text += f"• Format papier : <b>{paper_format}</b><br>"
        preview_text += "<br>"

        # Afficher le mode de fusion selon la checkbox
        split_files = self.split_files_checkbox.isChecked()
        if split_files:
            preview_text += "<i>📦 <b>Mode séparé :</b> Chaque fichier sera traité individuellement, trié séparément, puis juxtaposé avec une ligne vide entre chaque.</i>"
        else:
            preview_text += "<i>📦 <b>Mode fusionné :</b> Tous les fichiers seront fusionnés et triés globalement par référence (colonne A).</i>"

        self.print_preview_label.setText(preview_text)

    def toggle_header_fields(self, checked):
        """Active/désactive les champs d'en-tête selon la checkbox"""
        self.header_type_combo.setEnabled(checked)
        self.header_content_input.setEnabled(checked)

    def update_filename_example(self):
        """Met à jour l'exemple de nom de fichier"""
        from datetime import datetime

        # Récupérer le modèle
        template = self.output_filename_input.text() or "{supplier}_{date}"

        # Récupérer le format de date sélectionné
        date_format_text = self.date_format_combo.currentText()

        # Mapper le format
        date_formats = {
            "jj-mm-aa (15-01-25)": "%d-%m-%y",
            "jj-mm-aaaa (15-01-2025)": "%d-%m-%Y",
            "aaaa-mm-jj (2025-01-15)": "%Y-%m-%d",
            "aaaammjj (20250115)": "%Y%m%d",
            "jjmmaa (150125)": "%d%m%y",
            "jjmmaaaa (15012025)": "%d%m%Y"
        }

        # Obtenir le format Python correspondant
        python_format = date_formats.get(date_format_text, "%d-%m-%y")

        # Générer la date d'exemple
        date_str = datetime.now().strftime(python_format)
        time_str = datetime.now().strftime("%H%M%S")

        # Récupérer le format de sortie
        output_format = self.output_format_combo.currentText()

        # Remplacer les variables
        example = template.replace("{supplier}", "honda")
        example = example.replace("{date}", date_str)
        example = example.replace("{time}", time_str)

        # Ajouter l'extension
        example += f".{output_format}"

        self.filename_example.setText(f"<small><i>Exemple: {example}</i></small>")

    def load_logos_from_storage(self):
        """Charge la liste des logos depuis Supabase Storage"""
        try:
            # Récupérer la liste des fichiers du bucket supplier-logos
            response = supabase_client.client.storage.from_('supplier-logos').list()

            # Vider le combobox
            self.logo_combo.clear()
            self.logo_combo.addItem("(Aucun logo)", "")

            # Ajouter chaque logo
            for file_info in response:
                filename = file_info.get('name')
                if filename:
                    # Construire l'URL publique
                    public_url = supabase_client.client.storage.from_('supplier-logos').get_public_url(filename)

                    # Afficher le nom du fichier, stocker l'URL
                    self.logo_combo.addItem(filename, public_url)

            logger.info(f"{len(response)} logo(s) chargé(s) depuis Supabase Storage")

        except Exception as e:
            logger.error(f"Erreur chargement logos: {e}")
            # Ne pas afficher d'erreur à l'utilisateur, juste logger

    def load_supplier_data(self):
        """Charge les données du fournisseur"""
        if not self.supplier_data:
            return

        # Onglet général
        self.name_input.setText(self.supplier_data.get('name', ''))
        self.slug_input.setText(self.supplier_data.get('file_filter_slug', ''))

        # Logo - chercher dans le combo par URL
        logo_url = self.supplier_data.get('logo_url', '')
        if logo_url:
            index = self.logo_combo.findData(logo_url)
            if index >= 0:
                self.logo_combo.setCurrentIndex(index)

        self.active_checkbox.setChecked(self.supplier_data.get('active', True))

        # Coordonnées
        self.phone_input.setText(self.supplier_data.get('phone', ''))
        self.email_input.setText(self.supplier_data.get('email', ''))
        self.website_input.setText(self.supplier_data.get('website', ''))

        # Accès web
        self.web_user_input.setText(self.supplier_data.get('web_user', ''))
        self.web_password_input.setText(self.supplier_data.get('web_password', ''))

        # Patterns (JSON array)
        patterns = self.supplier_data.get('file_patterns', [])
        if patterns:
            self.patterns_input.setPlainText('\n'.join(patterns))

        # Onglet import
        import_config = self.supplier_data.get('import_config', {})
        if isinstance(import_config, dict):
            output_format = import_config.get('output_format', 'xlsx')
            index = self.output_format_combo.findText(output_format)
            if index >= 0:
                self.output_format_combo.setCurrentIndex(index)

            self.has_header_checkbox.setChecked(import_config.get('has_header', False))
            self.leading_zeros_checkbox.setChecked(import_config.get('leading_zeros', False))

            # En-tête du fichier généré
            add_output_header = import_config.get('add_output_header', False)
            self.add_output_header_checkbox.setChecked(add_output_header)

            header_type = import_config.get('header_type', 'Texte fixe')
            index = self.header_type_combo.findText(header_type)
            if index >= 0:
                self.header_type_combo.setCurrentIndex(index)

            self.header_content_input.setText(import_config.get('header_content', ''))

            # Doublons (rétrocompatibilité avec l'ancien nom de champ)
            merge_duplicates = import_config.get('merge_duplicates', import_config.get('check_duplicates', False))
            self.check_duplicates_checkbox.setChecked(merge_duplicates)

            # Colonnes à supprimer (cases à cocher)
            columns_to_remove_import = import_config.get('columns_to_remove', [])
            self.import_col_ref_checkbox.setChecked('ref' in columns_to_remove_import)
            self.import_col_qty_checkbox.setChecked('qty' in columns_to_remove_import)
            self.import_col_designation_checkbox.setChecked('designation' in columns_to_remove_import)
            self.import_col_price_checkbox.setChecked('price' in columns_to_remove_import)
            self.import_col_client_checkbox.setChecked('client' in columns_to_remove_import)
            self.import_col_ean13_checkbox.setChecked('ean13' in columns_to_remove_import)
            self.import_col_order_checkbox.setChecked('order' in columns_to_remove_import)

            # Préfixes à supprimer
            import_prefixes = import_config.get('prefixes_to_remove', [])
            if import_prefixes:
                self.import_prefix_input.setPlainText('\n'.join(import_prefixes))
            else:
                self.import_prefix_input.setPlainText('')

            # Format de date
            date_format = import_config.get('date_format', 'jj-mm-aa (15-01-25)')
            index = self.date_format_combo.findText(date_format)
            if index >= 0:
                self.date_format_combo.setCurrentIndex(index)

            # Nom du fichier de sortie
            self.output_filename_input.setText(import_config.get('output_filename', '{supplier}_{date}'))

            # Mettre à jour l'exemple de nom de fichier
            self.update_filename_example()

        # Onglet impression
        print_config = self.supplier_data.get('print_config', {})
        if isinstance(print_config, dict):
            # Colonnes à supprimer
            columns_to_remove = print_config.get('columns_to_remove', [])
            self.col_ref_checkbox.setChecked('ref' in columns_to_remove)
            self.col_qty_checkbox.setChecked('qty' in columns_to_remove)
            self.col_designation_checkbox.setChecked('designation' in columns_to_remove)
            self.col_price_checkbox.setChecked('price' in columns_to_remove)
            self.col_client_checkbox.setChecked('client' in columns_to_remove)
            self.col_ean13_checkbox.setChecked('ean13' in columns_to_remove)
            self.col_order_checkbox.setChecked('order' in columns_to_remove)

            # Préfixes (avec rétrocompatibilité pour l'ancien format)
            prefixes = print_config.get('prefixes_to_remove', [])
            if not prefixes:
                # Rétrocompatibilité: si l'ancien champ existe, l'utiliser
                old_prefix = print_config.get('prefix_to_remove', '')
                if old_prefix:
                    prefixes = [old_prefix]

            if prefixes:
                self.prefix_input.setPlainText('\n'.join(prefixes))
            else:
                self.prefix_input.setPlainText('')

            # Date
            self.add_date_checkbox.setChecked(print_config.get('add_date', False))

            # Séparation des fichiers
            self.split_files_checkbox.setChecked(print_config.get('split_files', False))

            # Format papier
            paper_format = print_config.get('paper_format', 'A4')
            index = self.print_format_combo.findText(paper_format)
            if index >= 0:
                self.print_format_combo.setCurrentIndex(index)

        # === Charger la configuration d'affichage ===
        display_config = self.supplier_data.get('display_config', {})
        if display_config:
            # Colonnes à supprimer pour affichage
            display_columns_to_remove = display_config.get('columns_to_remove', [])
            self.display_col_ref_checkbox.setChecked('ref' in display_columns_to_remove)
            self.display_col_qty_checkbox.setChecked('qty' in display_columns_to_remove)
            self.display_col_designation_checkbox.setChecked('designation' in display_columns_to_remove)
            self.display_col_price_checkbox.setChecked('price' in display_columns_to_remove)
            self.display_col_client_checkbox.setChecked('client' in display_columns_to_remove)
            self.display_col_ean13_checkbox.setChecked('ean13' in display_columns_to_remove)
            self.display_col_order_checkbox.setChecked('order' in display_columns_to_remove)

            # Préfixes pour affichage
            display_prefixes = display_config.get('prefixes_to_remove', [])
            if display_prefixes:
                self.display_prefix_input.setPlainText('\n'.join(display_prefixes))
            else:
                self.display_prefix_input.setPlainText('')

            # Date pour affichage
            self.display_add_date_checkbox.setChecked(display_config.get('add_date', False))

            # Séparation des fichiers pour affichage
            self.display_split_files_checkbox.setChecked(display_config.get('split_files', False))

        # === Charger la configuration Web ===
        web_config = self.supplier_data.get('web_config', {})
        if web_config:
            # URL
            self.web_url_input.setText(web_config.get('url', ''))

            # Code client
            client_code_enabled = web_config.get('client_code_enabled', False)
            self.web_client_code_enabled.setChecked(client_code_enabled)
            self.web_client_code_value.setText(web_config.get('client_code_value', ''))
            self.web_client_code_selector.setText(web_config.get('client_code_selector', ''))

            # Login
            self.web_login_value.setText(web_config.get('login_value', ''))
            self.web_login_selector.setText(web_config.get('login_selector', ''))

            # Mot de passe
            self.web_password_value.setText(web_config.get('password_value', ''))
            self.web_password_selector.setText(web_config.get('password_selector', ''))

            # Autre champ
            other_enabled = web_config.get('other_enabled', False)
            self.web_other_enabled.setChecked(other_enabled)
            self.web_other_value.setText(web_config.get('other_value', ''))
            self.web_other_selector.setText(web_config.get('other_selector', ''))

            # Bouton submit
            self.web_submit_selector.setText(web_config.get('submit_selector', ''))

            # Validation intermédiaire
            intermediate_enabled = web_config.get('intermediate_enabled', False)
            self.web_intermediate_enabled.setChecked(intermediate_enabled)
            self.web_intermediate_selector.setText(web_config.get('intermediate_selector', ''))

            # Cookie
            cookie_enabled = web_config.get('cookie_enabled', False)
            self.web_cookie_enabled.setChecked(cookie_enabled)
            self.web_cookie_selector.setText(web_config.get('cookie_selector', ''))

            # Captcha
            self.web_captcha_detect.setChecked(web_config.get('captcha_detect', False))

    def save_supplier(self):
        """Sauvegarde le fournisseur"""
        # Validation
        name = self.name_input.text().strip()
        slug = self.slug_input.text().strip()
        patterns_text = self.patterns_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Attention", "Le nom est obligatoire")
            return

        if not slug:
            QMessageBox.warning(self, "Attention", "Le slug de filtre est obligatoire")
            return

        if not patterns_text:
            QMessageBox.warning(self, "Attention", "Au moins un pattern de fichier est requis")
            return

        # Préparer les patterns
        patterns = [p.strip() for p in patterns_text.split('\n') if p.strip()]

        # Générer le code si nouveau
        if self.is_new:
            code = name.lower().replace(' ', '_').replace('-', '_')
            code = ''.join(c for c in code if c.isalnum() or c == '_')
        else:
            code = self.supplier_data.get('supplier_code', '')

        # Configuration d'import
        # Récupérer les colonnes à supprimer (via checkboxes)
        columns_to_remove_import = []
        if self.import_col_ref_checkbox.isChecked():
            columns_to_remove_import.append('ref')
        if self.import_col_qty_checkbox.isChecked():
            columns_to_remove_import.append('qty')
        if self.import_col_designation_checkbox.isChecked():
            columns_to_remove_import.append('designation')
        if self.import_col_price_checkbox.isChecked():
            columns_to_remove_import.append('price')
        if self.import_col_client_checkbox.isChecked():
            columns_to_remove_import.append('client')
        if self.import_col_ean13_checkbox.isChecked():
            columns_to_remove_import.append('ean13')
        if self.import_col_order_checkbox.isChecked():
            columns_to_remove_import.append('order')

        # Récupérer les préfixes d'import (un par ligne)
        import_prefixes_text = self.import_prefix_input.toPlainText().strip()
        import_prefixes_to_remove = [p.strip()[:8] for p in import_prefixes_text.split('\n') if p.strip()]  # Max 8 caractères par préfixe

        import_config = {
            'output_format': self.output_format_combo.currentText(),
            'has_header': self.has_header_checkbox.isChecked(),
            'leading_zeros': self.leading_zeros_checkbox.isChecked(),
            'add_output_header': self.add_output_header_checkbox.isChecked(),
            'header_type': self.header_type_combo.currentText(),
            'header_content': self.header_content_input.text().strip(),
            'merge_duplicates': self.check_duplicates_checkbox.isChecked(),  # Renommé pour clarté
            'columns_to_remove': columns_to_remove_import,
            'prefixes_to_remove': import_prefixes_to_remove,  # Préfixes à supprimer de la colonne Ref
            'output_filename': self.output_filename_input.text().strip() or '{supplier}_{date}',
            'date_format': self.date_format_combo.currentText()
        }

        # Configuration d'impression
        columns_to_remove = []
        if self.col_ref_checkbox.isChecked():
            columns_to_remove.append('ref')
        if self.col_qty_checkbox.isChecked():
            columns_to_remove.append('qty')
        if self.col_designation_checkbox.isChecked():
            columns_to_remove.append('designation')
        if self.col_price_checkbox.isChecked():
            columns_to_remove.append('price')
        if self.col_client_checkbox.isChecked():
            columns_to_remove.append('client')
        if self.col_ean13_checkbox.isChecked():
            columns_to_remove.append('ean13')
        if self.col_order_checkbox.isChecked():
            columns_to_remove.append('order')

        # Récupérer les préfixes (un par ligne)
        prefixes_text = self.prefix_input.toPlainText().strip()
        prefixes_to_remove = [p.strip()[:8] for p in prefixes_text.split('\n') if p.strip()]  # Max 8 caractères par préfixe

        print_config = {
            'columns_to_remove': columns_to_remove,
            'prefixes_to_remove': prefixes_to_remove,  # Nouveau: tableau de préfixes
            'add_date': self.add_date_checkbox.isChecked(),
            'split_files': self.split_files_checkbox.isChecked(),  # Séparer les fichiers avec lignes vides
            'paper_format': self.print_format_combo.currentText()
        }

        # Configuration d'affichage (pour le bouton Ouvrir)
        display_columns_to_remove = []
        if self.display_col_ref_checkbox.isChecked():
            display_columns_to_remove.append('ref')
        if self.display_col_qty_checkbox.isChecked():
            display_columns_to_remove.append('qty')
        if self.display_col_designation_checkbox.isChecked():
            display_columns_to_remove.append('designation')
        if self.display_col_price_checkbox.isChecked():
            display_columns_to_remove.append('price')
        if self.display_col_client_checkbox.isChecked():
            display_columns_to_remove.append('client')
        if self.display_col_ean13_checkbox.isChecked():
            display_columns_to_remove.append('ean13')
        if self.display_col_order_checkbox.isChecked():
            display_columns_to_remove.append('order')

        # Récupérer les préfixes d'affichage (un par ligne)
        display_prefixes_text = self.display_prefix_input.toPlainText().strip()
        display_prefixes_to_remove = [p.strip()[:8] for p in display_prefixes_text.split('\n') if p.strip()]

        display_config = {
            'columns_to_remove': display_columns_to_remove,
            'prefixes_to_remove': display_prefixes_to_remove,
            'add_date': self.display_add_date_checkbox.isChecked(),
            'split_files': self.display_split_files_checkbox.isChecked()
        }

        # Configuration Web (connexion automatique)
        web_config = {
            'url': self.web_url_input.text().strip(),
            'client_code_enabled': self.web_client_code_enabled.isChecked(),
            'client_code_value': self.web_client_code_value.text().strip(),
            'client_code_selector': self.web_client_code_selector.text().strip(),
            'login_value': self.web_login_value.text().strip(),
            'login_selector': self.web_login_selector.text().strip(),
            'password_value': self.web_password_value.text().strip(),
            'password_selector': self.web_password_selector.text().strip(),
            'other_enabled': self.web_other_enabled.isChecked(),
            'other_value': self.web_other_value.text().strip(),
            'other_selector': self.web_other_selector.text().strip(),
            'submit_selector': self.web_submit_selector.text().strip(),
            'intermediate_enabled': self.web_intermediate_enabled.isChecked(),
            'intermediate_selector': self.web_intermediate_selector.text().strip(),
            'cookie_enabled': self.web_cookie_enabled.isChecked(),
            'cookie_selector': self.web_cookie_selector.text().strip(),
            'captcha_detect': self.web_captcha_detect.isChecked()
        }

        # Récupérer l'URL du logo sélectionné
        logo_url = self.logo_combo.currentData()  # Récupère l'URL stockée dans le combo

        # Préparer les données
        data = {
            'supplier_code': code,
            'name': name,
            'file_filter_slug': slug,
            'logo_url': logo_url if logo_url else None,
            'phone': self.phone_input.text().strip() or None,
            'email': self.email_input.text().strip() or None,
            'website': self.website_input.text().strip() or None,
            'web_user': self.web_user_input.text().strip() or None,
            'web_password': self.web_password_input.text().strip() or None,
            'file_patterns': patterns,
            'active': self.active_checkbox.isChecked(),
            'import_config': import_config,
            'print_config': print_config,
            'display_config': display_config,
            'web_config': web_config
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
        self.setGeometry(100, 100, 1400, 700)

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
        add_btn.setStyleSheet("padding: 8px; font-weight: bold; background-color: #4CAF50; color: white;")
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
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Logo", "Nom", "Slug filtre", "Téléphone", "Email", "Site web",
            "Patterns", "Format sortie", "Actif", "Modifié", "ID"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setColumnHidden(10, True)  # ID caché

        # Hauteur des lignes pour les logos
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Largeurs colonnes
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Logo
        self.table.setColumnWidth(0, 50)  # Logo fixe à 50px
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Nom
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Slug
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Téléphone
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Email
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Site
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Patterns
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Format
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actif
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Modifié

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
                # Logo (colonne 0)
                logo_url = supplier.get('logo_url', '')
                if logo_url:
                    # Créer un label pour afficher l'image
                    logo_label = QLabel()
                    logo_label.setAlignment(Qt.AlignCenter)
                    logo_label.setScaledContents(False)

                    # Charger l'image de manière asynchrone
                    self._load_logo_image(logo_label, logo_url, 45)  # 45px pour s'adapter à la hauteur de 50px

                    self.table.setCellWidget(i, 0, logo_label)
                else:
                    # Pas de logo
                    empty_item = QTableWidgetItem("")
                    self.table.setItem(i, 0, empty_item)

                # Nom
                self.table.setItem(i, 1, QTableWidgetItem(supplier.get('name', '')))

                # Slug filtre
                slug = supplier.get('file_filter_slug', '')
                self.table.setItem(i, 2, QTableWidgetItem(slug if slug else '-'))

                # Téléphone
                phone = supplier.get('phone', '')
                self.table.setItem(i, 3, QTableWidgetItem(phone if phone else '-'))

                # Email
                email = supplier.get('email', '')
                self.table.setItem(i, 4, QTableWidgetItem(email if email else '-'))

                # Site web
                website = supplier.get('website', '')
                self.table.setItem(i, 5, QTableWidgetItem(website if website else '-'))

                # Patterns
                patterns = supplier.get('file_patterns', [])
                patterns_str = ', '.join(patterns[:2])  # 2 premiers
                if len(patterns) > 2:
                    patterns_str += f' +{len(patterns)-2}'
                self.table.setItem(i, 6, QTableWidgetItem(patterns_str))

                # Format sortie
                import_config = supplier.get('import_config', {})
                if isinstance(import_config, dict):
                    output_format = import_config.get('output_format', 'xlsx')
                else:
                    output_format = 'xlsx'
                self.table.setItem(i, 7, QTableWidgetItem(output_format.upper()))

                # Actif
                active = "✓" if supplier.get('active', False) else "✗"
                active_item = QTableWidgetItem(active)
                if supplier.get('active', False):
                    active_item.setForeground(Qt.darkGreen)
                else:
                    active_item.setForeground(Qt.red)
                self.table.setItem(i, 8, active_item)

                # Modifié
                updated = supplier.get('updated_at', '')
                if updated:
                    from datetime import datetime
                    dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                    updated_str = dt.strftime('%d/%m/%Y')
                else:
                    updated_str = '-'
                self.table.setItem(i, 9, QTableWidgetItem(updated_str))

                # ID (caché)
                self.table.setItem(i, 10, QTableWidgetItem(supplier.get('id', '')))

            self.count_label.setText(f"{len(self.suppliers_data)} fournisseur(s)")

            logger.info(f"{len(self.suppliers_data)} fournisseur(s) chargé(s)")

        except Exception as e:
            logger.error(f"Erreur chargement fournisseurs: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement:\n{str(e)}")

    def _load_logo_image(self, label: QLabel, url: str, size: int):
        """Charge et affiche une image de logo depuis une URL"""
        try:
            import requests
            from io import BytesIO

            # Télécharger l'image
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            # Charger dans QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)

            # Redimensionner en gardant les proportions
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    size, size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)
            else:
                logger.warning(f"Impossible de charger le logo: {url}")

        except Exception as e:
            logger.error(f"Erreur chargement logo {url}: {e}")

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
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        supplier_id = self.table.item(row, 10).text()  # Colonne 10 pour l'ID

        # Trouver les données complètes
        supplier_data = next((s for s in self.suppliers_data if s.get('id') == supplier_id), None)

        if supplier_data:
            dialog = SupplierEditorDialog(supplier_data=supplier_data, parent=self)

            if dialog.exec() == QDialog.Accepted:
                self.load_suppliers()
                self.suppliers_updated.emit()

    def delete_supplier(self):
        """Supprime le fournisseur sélectionné"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        supplier_name = self.table.item(row, 1).text()  # Colonne 1 pour le nom
        supplier_id = self.table.item(row, 10).text()  # Colonne 10 pour l'ID

        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer le fournisseur '{supplier_name}' ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                result = supabase_client.client.table('suppliers').delete().eq('id', supplier_id).execute()

                if result.data:
                    QMessageBox.information(self, "Succès", f"Fournisseur '{supplier_name}' supprimé")
                    self.load_suppliers()
                    self.suppliers_updated.emit()
                else:
                    QMessageBox.critical(self, "Erreur", "Échec de la suppression")

            except Exception as e:
                logger.error(f"Erreur suppression fournisseur: {e}")
                QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")
