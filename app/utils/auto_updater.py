"""
Système de mise à jour automatique de l'application
Télécharge et installe uniquement les fichiers modifiés
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from loguru import logger
from packaging import version

from app.version import __version__, GITHUB_REPO


class AutoUpdater:
    """Gestionnaire de mises à jour automatiques"""

    def __init__(self):
        self.current_version = __version__
        self.github_repo = GITHUB_REPO
        self.api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"

    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Vérifie si une mise à jour est disponible

        Returns:
            Dict contenant les infos de la mise à jour, ou None si pas de mise à jour
        """
        try:
            logger.info(f"Vérification des mises à jour... Version actuelle: {self.current_version}")

            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')

            logger.info(f"Dernière version disponible: {latest_version}")

            if version.parse(latest_version) > version.parse(self.current_version):
                return {
                    'version': latest_version,
                    'url': release_data['html_url'],
                    'download_url': self._get_installer_download_url(release_data),
                    'release_notes': release_data.get('body', ''),
                    'published_at': release_data.get('published_at', '')
                }

            logger.info("L'application est à jour")
            return None

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des mises à jour: {e}")
            return None

    def _get_installer_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """
        Extrait l'URL de téléchargement de l'installeur depuis les assets de la release

        Args:
            release_data: Données de la release GitHub

        Returns:
            URL de téléchargement de l'installeur, ou None si non trouvé
        """
        assets = release_data.get('assets', [])

        # Chercher l'installeur (priorité : Setup.exe, sinon .exe simple)
        for asset in assets:
            name = asset.get('name', '').lower()
            if 'setup' in name and name.endswith('.exe'):
                return asset.get('browser_download_url')

        # Fallback : prendre le premier .exe trouvé
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.exe'):
                return asset.get('browser_download_url')

        return None

    def download_update(self, download_url: str, progress_callback=None) -> Optional[Path]:
        """
        Télécharge l'installeur de mise à jour

        Args:
            download_url: URL de téléchargement
            progress_callback: Fonction callback pour le suivi de progression (pourcentage)

        Returns:
            Chemin du fichier téléchargé, ou None en cas d'erreur
        """
        try:
            logger.info(f"Téléchargement de la mise à jour depuis {download_url}")

            # Créer un fichier temporaire
            temp_dir = Path(tempfile.gettempdir()) / 'SupplierOrderManager'
            temp_dir.mkdir(exist_ok=True)

            filename = download_url.split('/')[-1]
            temp_file = temp_dir / filename

            # Télécharger avec suivi de progression
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            percentage = int((downloaded / total_size) * 100)
                            progress_callback(percentage)

            logger.info(f"Mise à jour téléchargée: {temp_file}")
            return temp_file

        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la mise à jour: {e}")
            return None

    def install_update(self, installer_path: Path) -> bool:
        """
        Lance l'installeur de mise à jour et quitte l'application

        Args:
            installer_path: Chemin de l'installeur téléchargé

        Returns:
            True si l'installation a été lancée, False sinon
        """
        try:
            logger.info(f"Lancement de l'installeur: {installer_path}")

            # Lancer l'installeur avec des arguments silencieux
            # L'installeur Inno Setup détectera et désinstallera l'ancienne version
            subprocess.Popen(
                [str(installer_path), '/SILENT', '/CLOSEAPPLICATIONS', '/RESTARTAPPLICATIONS'],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            )

            # Quitter l'application pour permettre la mise à jour
            logger.info("Application fermée pour permettre la mise à jour")
            return True

        except Exception as e:
            logger.error(f"Erreur lors du lancement de l'installeur: {e}")
            return False

    def check_and_prompt_update(self, parent_widget=None) -> Optional[Dict[str, Any]]:
        """
        Vérifie les mises à jour et retourne les infos si disponible

        Args:
            parent_widget: Widget parent pour les dialogues (optionnel)

        Returns:
            Informations de la mise à jour si disponible, None sinon
        """
        update_info = self.check_for_updates()

        if update_info:
            logger.info(f"Mise à jour disponible: v{update_info['version']}")
            return update_info

        return None


# Instance globale
auto_updater = AutoUpdater()
