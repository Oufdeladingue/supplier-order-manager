"""
Dialogue de réglages globaux de l'application
"""

import os
import sys
import json
from pathlib import Path
from loguru import logger
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QMessageBox, QSpinBox, QTabWidget, QWidget, QTextEdit,
    QScrollArea, QFrame, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.supabase_client import supabase_client
from app.utils import get_resource_path


class SettingsDialog(QDialog):
    """Dialogue pour les réglages globaux de l'application"""

    settings_updated = Signal()  # Signal émis quand les réglages sont mis à jour

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Réglages")
        self.setMinimumSize(700, 500)

        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # Titre
        title = QLabel("⚙️ Réglages de l'application")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Onglets
        tabs = QTabWidget()

        # Onglet 1: Connexion FTP
        ftp_tab = self.create_ftp_tab()
        tabs.addTab(ftp_tab, "🌐 Connexion FTP")

        # Onglet 2: Réglages du poste (préférences utilisateur)
        workstation_tab = self.create_workstation_tab()
        tabs.addTab(workstation_tab, "💻 Réglages du poste")

        # Onglet 3: À propos et mises à jour
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ️ À propos")

        layout.addWidget(tabs)

        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5abb44;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #186108;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def create_ftp_tab(self) -> QWidget:
        """Crée l'onglet de configuration FTP"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Scroll area pour le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # === Connexion FTP ===
        group_ftp = QGroupBox("Serveur FTP/SFTP")
        group_ftp.setStyleSheet("""
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
        ftp_layout = QVBoxLayout()

        # Hôte
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Hôte:"))
        self.ftp_host_input = QLineEdit()
        self.ftp_host_input.setPlaceholderText("ftp.exemple.com")
        host_layout.addWidget(self.ftp_host_input)
        ftp_layout.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.ftp_port_input = QSpinBox()
        self.ftp_port_input.setRange(1, 65535)
        self.ftp_port_input.setValue(22)
        port_layout.addWidget(self.ftp_port_input)
        port_layout.addStretch()
        ftp_layout.addLayout(port_layout)

        # Nom d'utilisateur
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Utilisateur:"))
        self.ftp_user_input = QLineEdit()
        self.ftp_user_input.setPlaceholderText("username")
        user_layout.addWidget(self.ftp_user_input)
        ftp_layout.addLayout(user_layout)

        # Mot de passe
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Mot de passe:"))
        self.ftp_pass_input = QLineEdit()
        self.ftp_pass_input.setEchoMode(QLineEdit.Password)
        self.ftp_pass_input.setPlaceholderText("••••••••")
        pass_layout.addWidget(self.ftp_pass_input)
        ftp_layout.addLayout(pass_layout)

        # Chemin distant
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Chemin distant:"))
        self.ftp_path_input = QLineEdit()
        self.ftp_path_input.setPlaceholderText("/chemin/vers/dossier")
        path_layout.addWidget(self.ftp_path_input)
        ftp_layout.addLayout(path_layout)

        # Bouton tester la connexion
        test_btn = QPushButton("🔌 Tester la connexion")
        test_btn.clicked.connect(self.test_ftp_connection)
        ftp_layout.addWidget(test_btn)

        group_ftp.setLayout(ftp_layout)
        content_layout.addWidget(group_ftp)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return widget

    def create_workstation_tab(self) -> QWidget:
        """Crée l'onglet Réglages du poste (préférences utilisateur)"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Description
        info_label = QLabel(
            "💻 <b>Réglages spécifiques à ce poste de travail</b><br>"
            "<small>Ces paramètres sont enregistrés localement et ne s'appliquent qu'à cet ordinateur.</small>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #E3F2FD; border-radius: 5px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # === Dossier de sortie par défaut ===
        group_output = QGroupBox("📁 Dossier de sortie par défaut")
        group_output.setStyleSheet("""
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
        output_layout = QVBoxLayout()

        output_help = QLabel(
            "<small>Dossier où seront enregistrés automatiquement les fichiers générés par l'application<br>"
            "(imports, impressions, exports, etc.)</small>"
        )
        output_help.setWordWrap(True)
        output_layout.addWidget(output_help)

        # Chemin du dossier
        folder_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setPlaceholderText("C:/Users/NomUtilisateur/Downloads")
        self.output_folder_input.setReadOnly(True)
        folder_layout.addWidget(self.output_folder_input)

        browse_btn = QPushButton("📂 Parcourir...")
        browse_btn.clicked.connect(self.browse_output_folder)
        folder_layout.addWidget(browse_btn)

        output_layout.addLayout(folder_layout)

        # Bouton réinitialiser
        reset_folder_btn = QPushButton("🔄 Utiliser le dossier Téléchargements par défaut")
        reset_folder_btn.clicked.connect(self.reset_output_folder)
        output_layout.addWidget(reset_folder_btn)

        group_output.setLayout(output_layout)
        layout.addWidget(group_output)

        # === Navigateur par défaut ===
        group_browser = QGroupBox("🌐 Navigateur par défaut")
        group_browser.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
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
        browser_layout = QVBoxLayout()

        browser_help = QLabel(
            "<small>Navigateur utilisé pour ouvrir les liens depuis l'application<br>"
            "(sites web fournisseurs, documentation, etc.)</small>"
        )
        browser_help.setWordWrap(True)
        browser_layout.addWidget(browser_help)

        # Sélection du navigateur
        browser_select_layout = QHBoxLayout()
        browser_select_layout.addWidget(QLabel("Navigateur:"))

        self.browser_combo = QComboBox()
        self.browser_combo.addItems([
            "Navigateur par défaut du système",
            "Google Chrome",
            "Mozilla Firefox",
            "Microsoft Edge",
            "Opera",
            "Brave",
            "Personnalisé..."
        ])
        browser_select_layout.addWidget(self.browser_combo)
        browser_select_layout.addStretch()
        browser_layout.addLayout(browser_select_layout)

        # Chemin personnalisé (affiché uniquement si "Personnalisé" est sélectionné)
        self.custom_browser_layout = QHBoxLayout()
        self.custom_browser_input = QLineEdit()
        self.custom_browser_input.setPlaceholderText("C:/Program Files/MonNavigateur/browser.exe")
        self.custom_browser_input.setEnabled(False)
        self.custom_browser_layout.addWidget(QLabel("Chemin:"))
        self.custom_browser_layout.addWidget(self.custom_browser_input)

        browse_browser_btn = QPushButton("📂")
        browse_browser_btn.setMaximumWidth(40)
        browse_browser_btn.clicked.connect(self.browse_browser_path)
        browse_browser_btn.setEnabled(False)
        self.browse_browser_btn = browse_browser_btn
        self.custom_browser_layout.addWidget(browse_browser_btn)

        browser_layout.addLayout(self.custom_browser_layout)

        # Connecter le changement de sélection
        self.browser_combo.currentTextChanged.connect(self.on_browser_changed)

        group_browser.setLayout(browser_layout)
        layout.addWidget(group_browser)

        # === Rafraîchissement automatique ===
        group_refresh = QGroupBox("🔄 Rafraîchissement automatique")
        group_refresh.setStyleSheet("""
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
        refresh_layout = QVBoxLayout()

        refresh_help = QLabel(
            "<small>Délai de rafraîchissement automatique de la liste des fichiers<br>"
            "(0 pour désactiver le rafraîchissement automatique)</small>"
        )
        refresh_help.setWordWrap(True)
        refresh_layout.addWidget(refresh_help)

        # Délai de rafraîchissement
        refresh_delay_layout = QHBoxLayout()
        refresh_delay_layout.addWidget(QLabel("Rafraîchir toutes les:"))

        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(0, 3600)  # 0 = désactivé, max 1 heure
        self.refresh_interval_spinbox.setValue(0)  # Désactivé par défaut
        self.refresh_interval_spinbox.setSuffix(" secondes")
        self.refresh_interval_spinbox.setSpecialValueText("Désactivé")
        refresh_delay_layout.addWidget(self.refresh_interval_spinbox)
        refresh_delay_layout.addStretch()
        refresh_layout.addLayout(refresh_delay_layout)

        group_refresh.setLayout(refresh_layout)
        layout.addWidget(group_refresh)

        layout.addStretch()

        return widget

    def on_browser_changed(self, text):
        """Active/désactive le champ personnalisé selon le navigateur sélectionné"""
        is_custom = text == "Personnalisé..."
        self.custom_browser_input.setEnabled(is_custom)
        self.browse_browser_btn.setEnabled(is_custom)

    def browse_browser_path(self):
        """Ouvre un dialogue pour sélectionner l'exécutable du navigateur"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner l'exécutable du navigateur",
            "C:/Program Files",
            "Exécutables (*.exe);;Tous les fichiers (*.*)"
        )
        if file_path:
            self.custom_browser_input.setText(file_path)

    def browse_output_folder(self):
        """Ouvre un dialogue pour sélectionner le dossier de sortie"""
        current_folder = self.output_folder_input.text() or str(Path.home() / "Downloads")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Sélectionner le dossier de sortie par défaut",
            current_folder
        )
        if folder:
            self.output_folder_input.setText(folder)

    def reset_output_folder(self):
        """Réinitialise le dossier de sortie au dossier Téléchargements"""
        default_folder = str(Path.home() / "Downloads")
        self.output_folder_input.setText(default_folder)

    def create_about_tab(self) -> QWidget:
        """Crée l'onglet À propos et mises à jour"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Logo et informations
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #5abb44;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)

        # Logo
        logo_path = get_resource_path("assets/logo/logo.png")
        if logo_path.exists():
            from PySide6.QtGui import QPixmap
            logo_label = QLabel()
            logo_pixmap = QPixmap(str(logo_path))
            scaled_logo = logo_pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(logo_label)

        # Nom de l'application
        app_name = QLabel("Gestionnaire de Commandes Fournisseurs")
        app_name.setStyleSheet("font-size: 14pt; font-weight: bold; color: #5abb44;")
        app_name.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(app_name)

        # Version
        version = QLabel(f"Version {os.getenv('APP_VERSION', '1.0.0')}")
        version.setStyleSheet("font-size: 11pt; color: #666;")
        version.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(version)

        # Description
        description = QLabel(
            "Application de gestion des commandes fournisseurs\n"
            "avec synchronisation FTP et impression automatisée"
        )
        description.setStyleSheet("font-size: 10pt; color: #666; padding: 10px;")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        info_layout.addWidget(description)

        layout.addWidget(info_frame)

        # Mises à jour
        updates_group = QGroupBox("Mises à jour")
        updates_group.setStyleSheet("""
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
        updates_layout = QVBoxLayout()

        update_info = QLabel("Vérifiez si une nouvelle version est disponible")
        update_info.setStyleSheet("color: #666; padding: 5px;")
        updates_layout.addWidget(update_info)

        check_update_btn = QPushButton("🔄 Vérifier les mises à jour")
        check_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        check_update_btn.clicked.connect(self.check_for_updates)
        updates_layout.addWidget(check_update_btn)

        updates_group.setLayout(updates_layout)
        layout.addWidget(updates_group)

        layout.addStretch()

        return widget

    def load_current_settings(self):
        """Charge les paramètres actuels depuis la base de données et le fichier local"""
        # === Paramètres globaux (BDD) ===
        try:
            # Récupérer tous les paramètres depuis la BDD
            response = supabase_client.client.table('app_settings').select('*').execute()

            if response.data:
                settings = {item['setting_key']: item['setting_value'] for item in response.data}

                # Charger les paramètres FTP
                self.ftp_host_input.setText(settings.get('ftp_host', ''))
                self.ftp_port_input.setValue(int(settings.get('ftp_port', '22')))
                self.ftp_user_input.setText(settings.get('ftp_username', ''))
                self.ftp_pass_input.setText(settings.get('ftp_password', ''))
                self.ftp_path_input.setText(settings.get('ftp_remote_path', ''))

                logger.info("Paramètres globaux chargés depuis la base de données")
            else:
                logger.warning("Aucun paramètre trouvé dans la base de données")

        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres globaux: {e}")
            # Fallback sur les variables d'environnement si la table n'existe pas encore
            self.ftp_host_input.setText(os.getenv("FTP_HOST", ""))
            self.ftp_port_input.setValue(int(os.getenv("FTP_PORT", "22")))
            self.ftp_user_input.setText(os.getenv("FTP_USERNAME", ""))
            self.ftp_pass_input.setText(os.getenv("FTP_PASSWORD", ""))
            self.ftp_path_input.setText(os.getenv("FTP_REMOTE_PATH", ""))

        # === Paramètres du poste (fichier local) ===
        try:
            config_file = Path.home() / '.supplier_order_manager' / 'workstation_config.json'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    local_settings = json.load(f)

                # Charger le dossier de sortie
                self.output_folder_input.setText(local_settings.get('output_folder', str(Path.home() / "Downloads")))

                # Charger le navigateur
                browser_choice = local_settings.get('browser', 'Navigateur par défaut du système')
                index = self.browser_combo.findText(browser_choice)
                if index >= 0:
                    self.browser_combo.setCurrentIndex(index)

                # Charger le chemin du navigateur personnalisé
                custom_browser_path = local_settings.get('custom_browser_path', '')
                if custom_browser_path:
                    self.custom_browser_input.setText(custom_browser_path)

                # Charger l'intervalle de rafraîchissement
                refresh_interval = local_settings.get('refresh_interval', 0)
                self.refresh_interval_spinbox.setValue(refresh_interval)

                logger.info("Paramètres du poste chargés depuis le fichier local")
            else:
                # Valeurs par défaut
                self.output_folder_input.setText(str(Path.home() / "Downloads"))

        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres du poste: {e}")
            self.output_folder_input.setText(str(Path.home() / "Downloads"))

    def save_settings(self):
        """Enregistre les paramètres dans la base de données et le fichier local"""
        try:
            # === Sauvegarder les paramètres globaux (BDD) ===
            settings_to_save = [
                ('ftp_host', self.ftp_host_input.text(), 'string'),
                ('ftp_port', str(self.ftp_port_input.value()), 'number'),
                ('ftp_username', self.ftp_user_input.text(), 'string'),
                ('ftp_password', self.ftp_pass_input.text(), 'string'),
                ('ftp_remote_path', self.ftp_path_input.text(), 'string'),
            ]

            # Sauvegarder chaque paramètre (upsert)
            for key, value, setting_type in settings_to_save:
                supabase_client.client.table('app_settings').upsert({
                    'setting_key': key,
                    'setting_value': value,
                    'setting_type': setting_type
                }, on_conflict='setting_key').execute()

            logger.info("Réglages globaux sauvegardés avec succès dans la base de données")

            # === Sauvegarder les paramètres du poste (fichier local) ===
            config_dir = Path.home() / '.supplier_order_manager'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'workstation_config.json'

            local_settings = {
                'output_folder': self.output_folder_input.text(),
                'browser': self.browser_combo.currentText(),
                'custom_browser_path': self.custom_browser_input.text() if self.browser_combo.currentText() == "Personnalisé..." else '',
                'refresh_interval': self.refresh_interval_spinbox.value()
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(local_settings, f, indent=2, ensure_ascii=False)

            logger.info(f"Réglages du poste sauvegardés dans {config_file}")

            QMessageBox.information(
                self,
                "Succès",
                "✅ Les réglages ont été enregistrés avec succès.\n\n"
                "• Réglages globaux (FTP): disponibles pour tous les utilisateurs\n"
                "• Réglages du poste: spécifiques à cet ordinateur"
            )

            self.settings_updated.emit()
            self.accept()

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des réglages: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"❌ Impossible de sauvegarder les réglages:\n{str(e)}"
            )

    def test_ftp_connection(self):
        """Teste la connexion FTP avec les paramètres saisis"""
        try:
            from worker.ftp_fetcher import FTPFetcher

            host = self.ftp_host_input.text()
            port = self.ftp_port_input.value()
            user = self.ftp_user_input.text()
            password = self.ftp_pass_input.text()

            if not all([host, user, password]):
                QMessageBox.warning(
                    self,
                    "Attention",
                    "Veuillez renseigner tous les champs obligatoires (hôte, utilisateur, mot de passe)"
                )
                return

            # Tenter la connexion
            fetcher = FTPFetcher(host, port, user, password, use_sftp=True)

            if fetcher.connect():
                fetcher.disconnect()
                QMessageBox.information(
                    self,
                    "Succès",
                    "✅ Connexion FTP réussie!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Échec",
                    "❌ Impossible de se connecter au serveur FTP.\n"
                    "Vérifiez vos paramètres de connexion."
                )

        except Exception as e:
            logger.error(f"Erreur lors du test de connexion FTP: {e}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du test de connexion:\n{str(e)}"
            )

    def check_for_updates(self):
        """Vérifie les mises à jour disponibles sur GitHub"""
        try:
            import requests
            from packaging import version

            # Récupérer la version actuelle
            import app.main as main_module
            current_version = main_module.__version__

            logger.info(f"Vérification des mises à jour... Version actuelle: {current_version}")

            # Interroger l'API GitHub pour la dernière release
            github_repo = "Oufdeladingue/supplier-order-manager"
            api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"

            response = requests.get(api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')  # Enlever le 'v' de 'v1.0.0'
            release_url = release_data['html_url']
            release_notes = release_data['body']

            logger.info(f"Dernière version disponible: {latest_version}")

            # Comparer les versions
            if version.parse(latest_version) > version.parse(current_version):
                # Une mise à jour est disponible
                message = (
                    f"🎉 Une nouvelle version est disponible !\n\n"
                    f"Version actuelle: v{current_version}\n"
                    f"Nouvelle version: v{latest_version}\n\n"
                    f"Notes de version:\n{release_notes[:300]}"
                    f"{'...' if len(release_notes) > 300 else ''}\n\n"
                    f"Voulez-vous télécharger la mise à jour ?"
                )

                reply = QMessageBox.question(
                    self,
                    "Mise à jour disponible",
                    message,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if reply == QMessageBox.Yes:
                    # Ouvrir la page de release dans le navigateur
                    import webbrowser
                    webbrowser.open(release_url)
                    logger.info(f"Ouverture de la page de release: {release_url}")
            else:
                # Déjà à jour
                QMessageBox.information(
                    self,
                    "Aucune mise à jour",
                    f"Version actuelle: v{current_version}\n\n"
                    "✅ Vous utilisez déjà la dernière version de l'application."
                )
                logger.info("Application déjà à jour")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur réseau lors de la vérification des mises à jour: {e}")
            QMessageBox.warning(
                self,
                "Erreur de connexion",
                f"Impossible de vérifier les mises à jour:\n\n"
                f"Vérifiez votre connexion Internet.\n\n"
                f"Erreur: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible de vérifier les mises à jour:\n{str(e)}"
            )
