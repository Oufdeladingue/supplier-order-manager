"""
Boîte de dialogue de connexion
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from loguru import logger
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.supabase_client import supabase_client


class LoginDialog(QDialog):
    """Dialogue de connexion à l'application"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connexion")
        self.setModal(True)
        self.setFixedSize(400, 200)

        self.init_ui()

    def init_ui(self):
        """Initialise l'interface"""
        layout = QVBoxLayout()

        # Titre
        title = QLabel("Gestionnaire de Commandes Fournisseurs")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Email ou Nom d'utilisateur
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email ou Nom d'utilisateur:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("nom.utilisateur ou email@entreprise.com")

        # Charger le dernier username utilisé
        last_username = self.load_last_username()
        if last_username:
            self.email_input.setText(last_username)
            logger.info(f"Dernier username chargé: {last_username}")

        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # Mot de passe
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Mot de passe:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.returnPressed.connect(self.login)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Boutons
        buttons_layout = QHBoxLayout()
        login_btn = QPushButton("Se connecter")
        login_btn.clicked.connect(self.login)
        login_btn.setDefault(True)
        buttons_layout.addWidget(login_btn)

        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def login(self):
        """Tente de se connecter"""
        identifier = self.email_input.text().strip()
        password = self.password_input.text()

        if not identifier or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return

        logger.info(f"Tentative de connexion pour: {identifier}")

        # Déterminer si c'est un email ou un username
        email = identifier
        if '@' not in identifier:
            # C'est un username, chercher l'email correspondant
            logger.info(f"Recherche de l'email pour le username: {identifier}")
            email = self.get_email_from_username(identifier)

            if not email:
                QMessageBox.critical(
                    self,
                    "Erreur de connexion",
                    f"Aucun utilisateur trouvé avec le nom d'utilisateur: {identifier}"
                )
                return

        # Tenter la connexion avec l'email
        result = supabase_client.sign_in(email, password)

        if result.get('success'):
            logger.info("Connexion réussie")
            # Sauvegarder le username pour la prochaine fois
            self.save_last_username(identifier)
            self.accept()
        else:
            error = result.get('error', 'Erreur inconnue')
            logger.error(f"Échec de connexion: {error}")
            QMessageBox.critical(self, "Erreur de connexion", f"Impossible de se connecter:\n{error}")

    def get_email_from_username(self, username: str) -> str:
        """Récupère l'email associé à un username depuis la base de données"""
        try:
            # Chercher dans la table profiles
            response = supabase_client.client.table('profiles').select('email').eq('username', username).execute()

            if response.data and len(response.data) > 0:
                email = response.data[0].get('email')
                logger.info(f"Email trouvé pour {username}: {email}")
                return email

            # Essayer aussi dans auth.users via la metadata
            # Si le username est stocké dans les métadonnées utilisateur
            logger.warning(f"Aucun email trouvé pour le username: {username}")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'email pour {username}: {e}")
            return None

    def load_last_username(self) -> str:
        """
        Charge le dernier username utilisé depuis le fichier de configuration local

        Returns:
            str: Le dernier username utilisé, ou None si aucun
        """
        try:
            config_file = Path.home() / '.supplier_order_manager' / 'workstation_config.json'

            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('last_username', None)

        except Exception as e:
            logger.error(f"Erreur lors du chargement du dernier username: {e}")

        return None

    def save_last_username(self, username: str):
        """
        Sauvegarde le username dans le fichier de configuration local

        Args:
            username: Le username à sauvegarder
        """
        try:
            config_dir = Path.home() / '.supplier_order_manager'
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / 'workstation_config.json'

            # Charger la config existante ou créer un nouveau dict
            config = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # Ajouter/mettre à jour le username
            config['last_username'] = username

            # Sauvegarder
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"Username sauvegardé: {username}")

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du username: {e}")
