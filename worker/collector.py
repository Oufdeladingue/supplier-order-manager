"""
Worker principal pour la collecte automatique des fichiers fournisseurs
À exécuter quotidiennement à 10h via Windows Task Scheduler
"""

import os
import sys
import json
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from worker.email_fetcher import EmailFetcher, ExchangeFetcher
from worker.ftp_fetcher import FTPFetcher
from app.services.supabase_client import supabase_client
from app.services.file_processor import FileProcessor
from app.models.file_record import FileType

# Charger les variables d'environnement
load_dotenv()

# Configuration du logger
logger.add("logs/collector_{time}.log", rotation="1 day", retention="30 days", level="INFO")


class SupplierFileCollector:
    """Collecteur automatique de fichiers fournisseurs"""

    def __init__(self):
        self.temp_folder = os.getenv("TEMP_FOLDER", "./temp")
        self.suppliers_config_path = "config/suppliers.json"
        self.file_processor = FileProcessor(self.temp_folder)
        self.collected_files: List[Dict[str, Any]] = []

    def load_suppliers_config(self) -> List[Dict[str, Any]]:
        """Charge la configuration des fournisseurs"""
        try:
            with open(self.suppliers_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('suppliers', [])
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config fournisseurs: {e}")
            return []

    def collect_from_email(self, supplier: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Collecte les fichiers depuis email pour un fournisseur"""
        logger.info(f"Collecte email pour: {supplier['name']}")

        try:
            # Choisir entre IMAP ou Exchange
            use_exchange = os.getenv("EXCHANGE_EMAIL") is not None

            if use_exchange:
                fetcher = ExchangeFetcher(
                    email=os.getenv("EXCHANGE_EMAIL"),
                    password=os.getenv("EXCHANGE_PASSWORD"),
                    server=os.getenv("EXCHANGE_SERVER", "outlook.office365.com")
                )
            else:
                fetcher = EmailFetcher(
                    host=os.getenv("EMAIL_HOST", "imap.gmail.com"),
                    port=int(os.getenv("EMAIL_PORT", 993)),
                    username=os.getenv("EMAIL_USERNAME"),
                    password=os.getenv("EMAIL_PASSWORD")
                )

            if not fetcher.connect():
                logger.error(f"Échec de connexion email pour {supplier['name']}")
                return []

            # Récupérer les pièces jointes
            files = fetcher.fetch_attachments(
                sender_filter=supplier.get('email_pattern'),
                target_date=target_date,
                output_folder=self.temp_folder
            )

            if not use_exchange:
                fetcher.disconnect()

            # Ajouter les infos du fournisseur
            for file in files:
                file['supplier_code'] = supplier['id']
                file['supplier_name'] = supplier['name']

            logger.info(f"{len(files)} fichier(s) collecté(s) par email pour {supplier['name']}")
            return files

        except Exception as e:
            logger.error(f"Erreur collecte email pour {supplier['name']}: {e}")
            return []

    def collect_from_ftp(self, supplier: Dict[str, Any], target_date: date) -> List[Dict[str, Any]]:
        """Collecte les fichiers depuis FTP pour un fournisseur"""
        logger.info(f"Collecte FTP pour: {supplier['name']}")

        try:
            ftp_config = supplier.get('ftp_config', {})

            if not ftp_config:
                logger.warning(f"Pas de config FTP pour {supplier['name']}")
                return []

            fetcher = FTPFetcher(
                host=ftp_config.get('host', os.getenv('FTP_HOST')),
                port=ftp_config.get('port', int(os.getenv('FTP_PORT', 22))),
                username=ftp_config.get('username', os.getenv('FTP_USERNAME')),
                password=ftp_config.get('password', os.getenv('FTP_PASSWORD')),
                use_sftp=ftp_config.get('use_sftp', True)
            )

            if not fetcher.connect():
                logger.error(f"Échec de connexion FTP pour {supplier['name']}")
                return []

            # Récupérer les fichiers
            files = fetcher.fetch_files_by_pattern(
                remote_path=supplier.get('ftp_path', '/'),
                file_patterns=supplier.get('file_patterns', ['*.csv', '*.xlsx']),
                target_date=target_date,
                output_folder=self.temp_folder
            )

            fetcher.disconnect()

            # Ajouter les infos du fournisseur
            for file in files:
                file['supplier_code'] = supplier['id']
                file['supplier_name'] = supplier['name']

            logger.info(f"{len(files)} fichier(s) collecté(s) par FTP pour {supplier['name']}")
            return files

        except Exception as e:
            logger.error(f"Erreur collecte FTP pour {supplier['name']}: {e}")
            return []

    def upload_to_supabase(self, file_info: Dict[str, Any]) -> bool:
        """Upload un fichier vers Supabase Storage et crée l'enregistrement DB"""
        try:
            # Lire le fichier
            file_path = Path(file_info['file_path'])
            with open(file_path, 'rb') as f:
                file_content = f.read()

            # Déterminer le type de fichier
            extension = file_path.suffix[1:].lower()
            if extension == 'csv':
                file_type = FileType.CSV
            elif extension == 'xlsx':
                file_type = FileType.XLSX
            elif extension == 'xls':
                file_type = FileType.XLS
            else:
                logger.warning(f"Type de fichier non supporté: {extension}")
                return False

            # Construire le chemin de stockage
            today = date.today().isoformat()
            storage_path = f"{file_info['supplier_code']}/{today}/{file_info['filename']}"

            # Upload vers Storage
            supabase_client.upload_file(
                bucket='supplier-files-original',
                file_path=storage_path,
                file_content=file_content
            )

            # Récupérer les infos du fichier
            file_details = self.file_processor.get_file_info(str(file_path), file_type)

            # Créer l'enregistrement dans la DB
            file_record = {
                'filename': file_info['filename'],
                'supplier_code': file_info['supplier_code'],
                'received_date': file_info['received_date'].isoformat(),
                'file_type': file_type.value,
                'status': 'pending',
                'original_path': storage_path,
                'file_size': file_info['file_size'],
                'row_count': file_details.get('row_count') if file_details else None
            }

            created = supabase_client.create_file(file_record)

            if created:
                logger.info(f"Fichier uploadé et enregistré: {file_info['filename']}")
                return True
            else:
                logger.error(f"Échec enregistrement DB pour: {file_info['filename']}")
                return False

        except Exception as e:
            logger.error(f"Erreur upload Supabase pour {file_info['filename']}: {e}")
            return False

    def run_collection(self, target_date: Optional[date] = None):
        """Lance la collecte pour tous les fournisseurs actifs"""
        if target_date is None:
            target_date = date.today()

        logger.info(f"=== Début de la collecte pour le {target_date} ===")

        # Charger la config des fournisseurs
        suppliers = self.load_suppliers_config()
        active_suppliers = [s for s in suppliers if s.get('active', True)]

        logger.info(f"{len(active_suppliers)} fournisseur(s) actif(s)")

        # Collecter pour chaque fournisseur
        for supplier in active_suppliers:
            source = supplier.get('source', 'email')

            if source == 'email':
                files = self.collect_from_email(supplier, target_date)
            elif source == 'ftp':
                files = self.collect_from_ftp(supplier, target_date)
            else:
                logger.warning(f"Source inconnue pour {supplier['name']}: {source}")
                continue

            # Uploader les fichiers vers Supabase
            for file_info in files:
                success = self.upload_to_supabase(file_info)
                if success:
                    self.collected_files.append(file_info)

        logger.info(f"=== Collecte terminée: {len(self.collected_files)} fichier(s) total ===")

        # Résumé
        self.print_summary()

    def print_summary(self):
        """Affiche un résumé de la collecte"""
        logger.info("=" * 50)
        logger.info("RÉSUMÉ DE LA COLLECTE")
        logger.info("=" * 50)

        if not self.collected_files:
            logger.info("Aucun fichier collecté")
            return

        # Grouper par fournisseur
        by_supplier = {}
        for file in self.collected_files:
            supplier = file['supplier_name']
            if supplier not in by_supplier:
                by_supplier[supplier] = []
            by_supplier[supplier].append(file['filename'])

        for supplier, files in by_supplier.items():
            logger.info(f"{supplier}: {len(files)} fichier(s)")
            for filename in files:
                logger.info(f"  - {filename}")

        logger.info("=" * 50)


def main():
    """Point d'entrée du script"""
    logger.info("Démarrage du collecteur de fichiers fournisseurs")

    try:
        collector = SupplierFileCollector()
        collector.run_collection()
    except Exception as e:
        logger.error(f"Erreur critique: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
