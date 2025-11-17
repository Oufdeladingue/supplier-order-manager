"""
Module pour récupérer les fichiers depuis un serveur FTP/SFTP
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pathlib import Path
from loguru import logger
import paramiko
from stat import S_ISDIR


class FTPFetcher:
    """Classe pour récupérer les fichiers depuis un serveur SFTP"""

    def __init__(self, host: str, port: int, username: str, password: str, use_sftp: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_sftp = use_sftp
        self.transport = None
        self.sftp = None

    def connect(self) -> bool:
        """Se connecte au serveur SFTP"""
        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logger.info(f"Connecté au serveur SFTP: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion SFTP: {e}")
            return False

    def disconnect(self):
        """Déconnecte du serveur"""
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
        logger.info("Déconnecté du serveur SFTP")

    def list_files(self, remote_path: str = "/", exclude_dirs: List[str] = None) -> List[Dict[str, Any]]:
        """Liste les fichiers dans un répertoire distant

        Args:
            remote_path: Chemin du répertoire distant
            exclude_dirs: Liste des sous-dossiers à exclure (ex: ['old', 'archives'])
        """
        if not self.sftp:
            logger.error("Pas de connexion SFTP active")
            return []

        if exclude_dirs is None:
            exclude_dirs = ['old']  # Par défaut, exclure le dossier 'old'

        try:
            files = []
            for entry in self.sftp.listdir_attr(remote_path):
                # Ignorer les dossiers exclus
                if S_ISDIR(entry.st_mode):
                    if entry.filename in exclude_dirs:
                        logger.debug(f"Dossier exclu: {entry.filename}")
                    continue

                # Ajouter uniquement les fichiers (pas les dossiers)
                if not S_ISDIR(entry.st_mode):
                    file_info = {
                        'filename': entry.filename,
                        'size': entry.st_size,
                        'modified': datetime.fromtimestamp(entry.st_mtime)
                    }
                    files.append(file_info)

            logger.info(f"{len(files)} fichier(s) trouvé(s) dans {remote_path} (dossiers exclus: {exclude_dirs})")
            return files
        except Exception as e:
            logger.error(f"Erreur lors du listage des fichiers: {e}")
            return []

    def download_file(self, remote_file: str, local_path: str) -> bool:
        """Télécharge un fichier depuis le serveur"""
        if not self.sftp:
            logger.error("Pas de connexion SFTP active")
            return False

        try:
            # Créer le dossier local si nécessaire
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            self.sftp.get(remote_file, local_path)
            logger.info(f"Fichier téléchargé: {remote_file} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de {remote_file}: {e}")
            return False

    def fetch_files_by_pattern(self, remote_path: str, file_patterns: List[str],
                              target_date: Optional[date] = None,
                              output_folder: str = "./temp") -> List[Dict[str, Any]]:
        """
        Télécharge les fichiers correspondant aux patterns

        Args:
            remote_path: Chemin distant du dossier
            file_patterns: Liste de patterns (ex: ["*.csv", "order_*.xlsx"])
            target_date: Date cible pour filtrer (optionnel)
            output_folder: Dossier local de destination

        Returns:
            Liste de dictionnaires contenant les informations des fichiers téléchargés
        """
        if not self.sftp:
            logger.error("Pas de connexion SFTP active")
            return []

        if target_date is None:
            target_date = date.today()

        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        try:
            # Lister tous les fichiers du répertoire
            all_files = self.list_files(remote_path)

            for file_info in all_files:
                filename = file_info['filename']

                # Vérifier si le fichier correspond aux patterns
                if not self._match_patterns(filename, file_patterns):
                    continue

                # Filtrer par date si spécifié
                if target_date:
                    file_date = file_info['modified'].date()
                    if file_date != target_date:
                        continue

                # Télécharger le fichier
                remote_file = f"{remote_path}/{filename}".replace('//', '/')
                local_file = output_path / filename

                if self.download_file(remote_file, str(local_file)):
                    downloaded_files.append({
                        'filename': filename,
                        'file_path': str(local_file),
                        'file_size': file_info['size'],
                        'modified_date': file_info['modified'],
                        'received_date': target_date,
                        'source': 'ftp'
                    })

            logger.info(f"Total de fichiers téléchargés depuis FTP: {len(downloaded_files)}")
            return downloaded_files

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des fichiers FTP: {e}")
            return downloaded_files

    def _match_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Vérifie si un nom de fichier correspond à un des patterns"""
        import fnmatch

        for pattern in patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def upload_file(self, local_file: str, remote_path: str) -> bool:
        """
        Upload un fichier vers le serveur SFTP
        Utile pour envoyer les fichiers transformés aux fournisseurs
        """
        if not self.sftp:
            logger.error("Pas de connexion SFTP active")
            return False

        try:
            self.sftp.put(local_file, remote_path)
            logger.info(f"Fichier uploadé: {local_file} -> {remote_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'upload de {local_file}: {e}")
            return False

    def move_to_archive(self, remote_file: str, archive_folder: str = "old") -> bool:
        """
        Déplace un fichier vers le dossier d'archives après traitement

        Args:
            remote_file: Chemin complet du fichier source
            archive_folder: Nom du sous-dossier d'archives (défaut: 'old')

        Returns:
            True si le déplacement a réussi
        """
        if not self.sftp:
            logger.error("Pas de connexion SFTP active")
            return False

        try:
            # Extraire le chemin parent et le nom de fichier (utiliser des opérations sur chaînes pour garder les slashes Unix)
            # Exemple: /home/mjard_ep43/export-cdes-fournisseurs/M-Jardin Bleu-13-11-25.csv
            if '/' in remote_file:
                parent_dir, filename = remote_file.rsplit('/', 1)
            else:
                parent_dir = ''
                filename = remote_file

            # Construire le chemin du dossier d'archives (format Unix)
            if parent_dir:
                archive_path = f"{parent_dir}/{archive_folder}"
            else:
                archive_path = archive_folder

            logger.info(f"Chemins: parent_dir='{parent_dir}', archive_path='{archive_path}', filename='{filename}'")

            # Construire le chemin de destination
            destination = f"{archive_path}/{filename}"

            # Déplacer le fichier (renommer)
            self.sftp.rename(remote_file, destination)

            logger.info(f"Fichier archivé: {remote_file} -> {destination}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'archivage de {remote_file}: {e}")
            return False
