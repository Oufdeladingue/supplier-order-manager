"""
Interface de gestion des fichiers SFTP
Permet de naviguer, déplacer, renommer et supprimer des fichiers sur le serveur
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from loguru import logger

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QInputDialog,
    QGroupBox, QLineEdit, QMenu, QSplitter, QTextEdit, QComboBox,
    QCheckBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIcon, QAction

import paramiko
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent.parent))

load_dotenv()


class SFTPWorker(QThread):
    """Worker thread pour les opérations SFTP"""

    finished = Signal(bool, str)  # success, message
    progress = Signal(str)  # message de progression

    def __init__(self, operation: str, params: Dict):
        super().__init__()
        self.operation = operation
        self.params = params
        self.sftp = None
        self.transport = None

    def run(self):
        """Execute l'opération SFTP"""
        try:
            # Connexion SFTP
            self.progress.emit("Connexion au serveur SFTP...")
            self.connect_sftp()

            # Exécuter l'opération
            if self.operation == "list":
                result = self.list_directory()
            elif self.operation == "move":
                result = self.move_file()
            elif self.operation == "rename":
                result = self.rename_file()
            elif self.operation == "delete":
                result = self.delete_file()
            elif self.operation == "mkdir":
                result = self.create_directory()
            else:
                raise ValueError(f"Opération inconnue: {self.operation}")

            self.finished.emit(True, result)

        except Exception as e:
            logger.error(f"Erreur SFTP {self.operation}: {e}")
            self.finished.emit(False, str(e))

        finally:
            self.disconnect_sftp()

    def connect_sftp(self):
        """Connexion au serveur SFTP"""
        host = os.getenv("FTP_HOST")
        port = int(os.getenv("FTP_PORT", 22))
        username = os.getenv("FTP_USERNAME")
        password = os.getenv("FTP_PASSWORD")

        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def disconnect_sftp(self):
        """Déconnexion SFTP"""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()

    def list_directory(self) -> str:
        """Liste les fichiers d'un répertoire"""
        path = self.params.get('path', '/')
        files = self.sftp.listdir_attr(path)
        return str(len(files))

    def move_file(self) -> str:
        """Déplace un fichier"""
        src = self.params['source']
        dst = self.params['destination']

        self.progress.emit(f"Déplacement de {src} vers {dst}...")
        self.sftp.rename(src, dst)

        return f"Fichier déplacé: {Path(src).name} → {Path(dst).parent}"

    def rename_file(self) -> str:
        """Renomme un fichier"""
        old_path = self.params['old_path']
        new_path = self.params['new_path']

        self.progress.emit(f"Renommage de {old_path}...")
        self.sftp.rename(old_path, new_path)

        return f"Fichier renommé: {Path(old_path).name} → {Path(new_path).name}"

    def delete_file(self) -> str:
        """Supprime un fichier"""
        path = self.params['path']

        self.progress.emit(f"Suppression de {path}...")

        try:
            # Essayer de supprimer comme fichier
            self.sftp.remove(path)
            return f"Fichier supprimé: {Path(path).name}"
        except:
            # Essayer de supprimer comme dossier
            self.sftp.rmdir(path)
            return f"Dossier supprimé: {Path(path).name}"

    def create_directory(self) -> str:
        """Crée un répertoire"""
        path = self.params['path']

        self.progress.emit(f"Création du dossier {path}...")
        self.sftp.mkdir(path)

        return f"Dossier créé: {Path(path).name}"


class FTPManagerDialog(QDialog):
    """
    Interface de gestion des fichiers SFTP
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = os.getenv("FTP_PATH", "/")
        self.files_cache = {}

        self.init_ui()
        self.load_directory(self.current_path)

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Gestionnaire de Fichiers SFTP")
        self.setGeometry(100, 100, 1200, 800)

        layout = QVBoxLayout(self)

        # Section navigation
        nav_section = self.create_navigation_section()
        layout.addWidget(nav_section)

        # Section principale avec arborescence
        main_section = self.create_main_section()
        layout.addWidget(main_section, stretch=1)

        # Section actions automatiques
        auto_section = self.create_auto_actions_section()
        layout.addWidget(auto_section)

        # Boutons
        buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(lambda: self.load_directory(self.current_path))
        buttons_layout.addWidget(refresh_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def create_navigation_section(self) -> QGroupBox:
        """Crée la section de navigation"""
        group = QGroupBox("Navigation")
        layout = QHBoxLayout()

        # Chemin actuel
        layout.addWidget(QLabel("Chemin:"))

        self.path_input = QLineEdit()
        self.path_input.setText(self.current_path)
        self.path_input.returnPressed.connect(self.navigate_to_path)
        layout.addWidget(self.path_input, stretch=1)

        # Bouton Go
        go_btn = QPushButton("→")
        go_btn.clicked.connect(self.navigate_to_path)
        layout.addWidget(go_btn)

        # Bouton Parent
        parent_btn = QPushButton("⬆ Parent")
        parent_btn.clicked.connect(self.navigate_to_parent)
        layout.addWidget(parent_btn)

        # Bouton Nouveau dossier
        mkdir_btn = QPushButton("📁 Nouveau Dossier")
        mkdir_btn.clicked.connect(self.create_new_directory)
        layout.addWidget(mkdir_btn)

        group.setLayout(layout)
        return group

    def create_main_section(self) -> QWidget:
        """Crée la section principale avec l'arborescence"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Label info
        self.info_label = QLabel("Chargement...")
        layout.addWidget(self.info_label)

        # Arborescence des fichiers
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabels(["Nom", "Type", "Taille", "Date"])
        self.files_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.files_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.files_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.files_tree.setColumnWidth(0, 400)
        layout.addWidget(self.files_tree)

        return widget

    def create_auto_actions_section(self) -> QGroupBox:
        """Crée la section des actions automatiques"""
        group = QGroupBox("Actions Automatiques Après Traitement")
        layout = QVBoxLayout()

        # Checkbox activation
        self.auto_move_enabled = QCheckBox("Déplacer automatiquement les fichiers traités")
        self.auto_move_enabled.stateChanged.connect(self.on_auto_move_toggled)
        layout.addWidget(self.auto_move_enabled)

        # Configuration destination
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Dossier de destination:"))

        self.auto_move_dest = QLineEdit()
        self.auto_move_dest.setPlaceholderText("/home/mjard_ep43/archives")
        self.auto_move_dest.setEnabled(False)
        dest_layout.addWidget(self.auto_move_dest, stretch=1)

        browse_btn = QPushButton("📁")
        browse_btn.clicked.connect(self.browse_auto_move_destination)
        browse_btn.setEnabled(False)
        dest_layout.addWidget(browse_btn)
        self.auto_move_browse_btn = browse_btn

        layout.addLayout(dest_layout)

        # Pattern de fichiers
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Appliquer aux fichiers:"))

        self.auto_move_pattern = QComboBox()
        self.auto_move_pattern.addItems([
            "Tous les fichiers",
            "Fichiers Honda uniquement",
            "Fichiers Stihl uniquement",
            "Fichiers de la journée",
            "Pattern personnalisé..."
        ])
        self.auto_move_pattern.setEnabled(False)
        pattern_layout.addWidget(self.auto_move_pattern, stretch=1)

        layout.addLayout(pattern_layout)

        # Bouton sauvegarder config
        save_config_btn = QPushButton("💾 Sauvegarder Configuration Auto")
        save_config_btn.clicked.connect(self.save_auto_move_config)
        save_config_btn.setEnabled(False)
        layout.addWidget(save_config_btn)
        self.save_auto_config_btn = save_config_btn

        group.setLayout(layout)
        return group

    def on_auto_move_toggled(self, state):
        """Active/désactive les options de déplacement automatique"""
        enabled = state == Qt.Checked
        self.auto_move_dest.setEnabled(enabled)
        self.auto_move_browse_btn.setEnabled(enabled)
        self.auto_move_pattern.setEnabled(enabled)
        self.save_auto_config_btn.setEnabled(enabled)

    def browse_auto_move_destination(self):
        """Permet de choisir le dossier de destination"""
        # Pour l'instant, on utilise un input dialog
        # Plus tard, on pourrait faire un vrai navigateur de dossiers SFTP
        path, ok = QInputDialog.getText(
            self,
            "Dossier de destination",
            "Entrez le chemin du dossier de destination:",
            text=self.auto_move_dest.text()
        )

        if ok and path:
            self.auto_move_dest.setText(path)

    def save_auto_move_config(self):
        """Sauvegarde la configuration de déplacement automatique"""
        try:
            import json

            config = {
                "enabled": self.auto_move_enabled.isChecked(),
                "destination": self.auto_move_dest.text(),
                "pattern": self.auto_move_pattern.currentText()
            }

            config_path = Path(__file__).parent.parent.parent / "config" / "auto_move.json"

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self,
                "Succès",
                "Configuration sauvegardée!\n\n"
                "Les fichiers seront automatiquement déplacés après traitement."
            )

        except Exception as e:
            logger.error(f"Erreur sauvegarde config auto-move: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")

    def load_directory(self, path: str):
        """Charge le contenu d'un répertoire"""
        self.info_label.setText(f"Chargement de {path}...")
        self.files_tree.clear()

        # Lancer le worker SFTP
        worker = SFTPWorker("list", {"path": path})
        worker.progress.connect(self.on_worker_progress)
        worker.finished.connect(lambda success, msg: self.on_directory_loaded(success, msg, path))
        worker.start()

        # Stocker le worker pour éviter qu'il soit supprimé
        self.current_worker = worker

    def on_worker_progress(self, message: str):
        """Affiche la progression"""
        self.info_label.setText(message)

    def on_directory_loaded(self, success: bool, message: str, path: str):
        """Appelé quand le répertoire est chargé"""
        if not success:
            QMessageBox.critical(self, "Erreur", f"Erreur chargement:\n{message}")
            self.info_label.setText(f"Erreur: {message}")
            return

        # Recharger les fichiers avec une connexion directe
        try:
            host = os.getenv("FTP_HOST")
            port = int(os.getenv("FTP_PORT", 22))
            username = os.getenv("FTP_USERNAME")
            password = os.getenv("FTP_PASSWORD")

            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            files = sftp.listdir_attr(path)

            self.files_tree.clear()

            for file_attr in files:
                file_name = file_attr.filename
                is_dir = file_attr.st_mode & 0o040000  # Check if directory

                item = QTreeWidgetItem(self.files_tree)

                # Nom
                if is_dir:
                    item.setText(0, f"📁 {file_name}")
                    item.setData(0, Qt.UserRole, "directory")
                else:
                    item.setText(0, f"📄 {file_name}")
                    item.setData(0, Qt.UserRole, "file")

                # Type
                item.setText(1, "Dossier" if is_dir else "Fichier")

                # Taille
                if not is_dir:
                    size_mb = file_attr.st_size / (1024 * 1024)
                    item.setText(2, f"{size_mb:.2f} MB")

                # Date
                try:
                    mtime = datetime.fromtimestamp(file_attr.st_mtime)
                    item.setText(3, mtime.strftime("%Y-%m-%d %H:%M"))
                except:
                    pass

                # Stocker le chemin complet
                full_path = f"{path}/{file_name}".replace('//', '/')
                item.setData(1, Qt.UserRole, full_path)

            sftp.close()
            transport.close()

            self.current_path = path
            self.path_input.setText(path)
            self.info_label.setText(f"{len(files)} élément(s) dans {path}")

        except Exception as e:
            logger.error(f"Erreur chargement fichiers: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")

    def navigate_to_path(self):
        """Navigue vers le chemin saisi"""
        path = self.path_input.text().strip()
        if path:
            self.load_directory(path)

    def navigate_to_parent(self):
        """Navigue vers le dossier parent"""
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:
            self.load_directory(parent)

    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Appelé lors du double-clic sur un élément"""
        item_type = item.data(0, Qt.UserRole)

        if item_type == "directory":
            # Naviguer dans le dossier
            full_path = item.data(1, Qt.UserRole)
            self.load_directory(full_path)

    def show_context_menu(self, position):
        """Affiche le menu contextuel"""
        item = self.files_tree.itemAt(position)

        if not item:
            return

        menu = QMenu()

        # Actions selon le type
        item_type = item.data(0, Qt.UserRole)
        full_path = item.data(1, Qt.UserRole)

        # Déplacer
        move_action = QAction("📦 Déplacer vers...", self)
        move_action.triggered.connect(lambda: self.move_item(full_path))
        menu.addAction(move_action)

        # Renommer
        rename_action = QAction("✏️ Renommer", self)
        rename_action.triggered.connect(lambda: self.rename_item(full_path))
        menu.addAction(rename_action)

        menu.addSeparator()

        # Supprimer
        delete_action = QAction("🗑️ Supprimer", self)
        delete_action.triggered.connect(lambda: self.delete_item(full_path, item_type))
        menu.addAction(delete_action)

        menu.exec_(self.files_tree.viewport().mapToGlobal(position))

    def create_new_directory(self):
        """Crée un nouveau dossier"""
        name, ok = QInputDialog.getText(
            self,
            "Nouveau dossier",
            "Nom du dossier:"
        )

        if not ok or not name:
            return

        new_path = f"{self.current_path}/{name}".replace('//', '/')

        worker = SFTPWorker("mkdir", {"path": new_path})
        worker.progress.connect(self.on_worker_progress)
        worker.finished.connect(lambda success, msg: self.on_operation_finished(success, msg))
        worker.start()

        self.current_worker = worker

    def move_item(self, source_path: str):
        """Déplace un élément"""
        dest_path, ok = QInputDialog.getText(
            self,
            "Déplacer",
            "Destination (chemin complet):",
            text=f"{Path(source_path).parent}/{Path(source_path).name}"
        )

        if not ok or not dest_path:
            return

        worker = SFTPWorker("move", {"source": source_path, "destination": dest_path})
        worker.progress.connect(self.on_worker_progress)
        worker.finished.connect(lambda success, msg: self.on_operation_finished(success, msg))
        worker.start()

        self.current_worker = worker

    def rename_item(self, old_path: str):
        """Renomme un élément"""
        old_name = Path(old_path).name
        new_name, ok = QInputDialog.getText(
            self,
            "Renommer",
            "Nouveau nom:",
            text=old_name
        )

        if not ok or not new_name or new_name == old_name:
            return

        new_path = f"{Path(old_path).parent}/{new_name}"

        worker = SFTPWorker("rename", {"old_path": old_path, "new_path": new_path})
        worker.progress.connect(self.on_worker_progress)
        worker.finished.connect(lambda success, msg: self.on_operation_finished(success, msg))
        worker.start()

        self.current_worker = worker

    def delete_item(self, path: str, item_type: str):
        """Supprime un élément"""
        name = Path(path).name
        type_str = "dossier" if item_type == "directory" else "fichier"

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce {type_str}?\n\n{name}",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        worker = SFTPWorker("delete", {"path": path})
        worker.progress.connect(self.on_worker_progress)
        worker.finished.connect(lambda success, msg: self.on_operation_finished(success, msg))
        worker.start()

        self.current_worker = worker

    def on_operation_finished(self, success: bool, message: str):
        """Appelé quand une opération est terminée"""
        if success:
            QMessageBox.information(self, "Succès", message)
            self.load_directory(self.current_path)
        else:
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{message}")

        self.info_label.setText(message if success else f"Erreur: {message}")
