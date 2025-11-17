"""
Module pour récupérer les fichiers depuis une boîte email
Support IMAP et Exchange
"""

import os
import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pathlib import Path
from loguru import logger


class EmailFetcher:
    """Classe pour récupérer les fichiers depuis une boîte email IMAP"""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Se connecte au serveur IMAP"""
        try:
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            self.connection.login(self.username, self.password)
            logger.info(f"Connecté au serveur email: {self.host}")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion email: {e}")
            return False

    def disconnect(self):
        """Déconnecte du serveur"""
        if self.connection:
            try:
                self.connection.logout()
                logger.info("Déconnecté du serveur email")
            except Exception as e:
                logger.error(f"Erreur lors de la déconnexion: {e}")

    def fetch_attachments(self, sender_filter: Optional[str] = None,
                         subject_filter: Optional[str] = None,
                         target_date: Optional[date] = None,
                         output_folder: str = "./temp") -> List[Dict[str, Any]]:
        """
        Récupère les pièces jointes des emails

        Args:
            sender_filter: Filtre sur l'expéditeur (ex: "fournisseur@email.com")
            subject_filter: Filtre sur le sujet
            target_date: Date cible (par défaut aujourd'hui)
            output_folder: Dossier où sauvegarder les fichiers

        Returns:
            Liste de dictionnaires contenant les informations des fichiers téléchargés
        """
        if not self.connection:
            logger.error("Pas de connexion active")
            return []

        if target_date is None:
            target_date = date.today()

        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        try:
            # Sélectionner la boîte de réception
            self.connection.select("INBOX")

            # Construire la requête de recherche
            date_str = target_date.strftime("%d-%b-%Y")
            search_criteria = f'(ON {date_str})'

            if sender_filter:
                search_criteria = f'{search_criteria} FROM "{sender_filter}"'

            logger.info(f"Recherche d'emails avec critères: {search_criteria}")

            # Rechercher les emails
            status, messages = self.connection.search(None, search_criteria)

            if status != "OK":
                logger.warning("Aucun email trouvé")
                return []

            email_ids = messages[0].split()
            logger.info(f"{len(email_ids)} email(s) trouvé(s)")

            # Parcourir chaque email
            for email_id in email_ids:
                status, msg_data = self.connection.fetch(email_id, "(RFC822)")

                if status != "OK":
                    continue

                # Parser l'email
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Récupérer le sujet
                        subject = self._decode_header_value(msg.get("Subject", ""))

                        # Filtrer par sujet si nécessaire
                        if subject_filter and subject_filter.lower() not in subject.lower():
                            continue

                        # Récupérer l'expéditeur
                        from_email = self._decode_header_value(msg.get("From", ""))

                        logger.debug(f"Traitement email: {subject} de {from_email}")

                        # Parcourir les pièces jointes
                        for part in msg.walk():
                            if part.get_content_maintype() == 'multipart':
                                continue
                            if part.get('Content-Disposition') is None:
                                continue

                            filename = part.get_filename()
                            if filename:
                                filename = self._decode_header_value(filename)

                                # Vérifier si c'est un fichier CSV ou Excel
                                if not (filename.endswith('.csv') or
                                       filename.endswith('.xlsx') or
                                       filename.endswith('.xls')):
                                    continue

                                # Sauvegarder la pièce jointe
                                file_path = output_path / filename
                                with open(file_path, 'wb') as f:
                                    f.write(part.get_payload(decode=True))

                                file_size = file_path.stat().st_size

                                downloaded_files.append({
                                    'filename': filename,
                                    'file_path': str(file_path),
                                    'file_size': file_size,
                                    'sender': from_email,
                                    'subject': subject,
                                    'received_date': target_date,
                                    'source': 'email'
                                })

                                logger.info(f"Fichier téléchargé: {filename} ({file_size} bytes)")

            logger.info(f"Total de fichiers téléchargés: {len(downloaded_files)}")
            return downloaded_files

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des pièces jointes: {e}")
            return downloaded_files

    def _decode_header_value(self, value: str) -> str:
        """Décode les valeurs d'en-tête email"""
        if not value:
            return ""

        decoded_parts = decode_header(value)
        decoded_value = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_value += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_value += part

        return decoded_value


class ExchangeFetcher:
    """
    Classe pour récupérer les fichiers depuis Exchange Server
    Nécessite la librairie exchangelib
    """

    def __init__(self, email: str, password: str, server: str = "outlook.office365.com"):
        self.email = email
        self.password = password
        self.server = server
        self.account = None

    def connect(self) -> bool:
        """Se connecte au serveur Exchange"""
        try:
            from exchangelib import Credentials, Account, Configuration

            credentials = Credentials(self.email, self.password)
            config = Configuration(server=self.server, credentials=credentials)
            self.account = Account(
                primary_smtp_address=self.email,
                config=config,
                autodiscover=False,
                access_type='IMPERSONATION'
            )
            logger.info(f"Connecté à Exchange: {self.email}")
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion Exchange: {e}")
            return False

    def fetch_attachments(self, sender_filter: Optional[str] = None,
                         subject_filter: Optional[str] = None,
                         target_date: Optional[date] = None,
                         output_folder: str = "./temp") -> List[Dict[str, Any]]:
        """
        Récupère les pièces jointes depuis Exchange

        Args similaires à EmailFetcher.fetch_attachments
        """
        if not self.account:
            logger.error("Pas de connexion Exchange active")
            return []

        if target_date is None:
            target_date = date.today()

        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded_files = []

        try:
            from exchangelib import Q
            from datetime import datetime as dt, timedelta

            # Créer la plage de dates pour aujourd'hui
            start_date = dt.combine(target_date, dt.min.time())
            end_date = start_date + timedelta(days=1)

            # Construire le filtre
            query = Q(datetime_received__range=(start_date, end_date))

            if sender_filter:
                query &= Q(sender__email_address=sender_filter)

            if subject_filter:
                query &= Q(subject__icontains=subject_filter)

            # Rechercher les emails
            items = self.account.inbox.filter(query).order_by('-datetime_received')

            logger.info(f"Recherche d'emails Exchange pour {target_date}")

            for item in items:
                # Parcourir les pièces jointes
                for attachment in item.attachments:
                    if hasattr(attachment, 'name'):
                        filename = attachment.name

                        # Vérifier si c'est un fichier CSV ou Excel
                        if not (filename.endswith('.csv') or
                               filename.endswith('.xlsx') or
                               filename.endswith('.xls')):
                            continue

                        # Sauvegarder la pièce jointe
                        file_path = output_path / filename
                        with open(file_path, 'wb') as f:
                            f.write(attachment.content)

                        file_size = file_path.stat().st_size

                        downloaded_files.append({
                            'filename': filename,
                            'file_path': str(file_path),
                            'file_size': file_size,
                            'sender': str(item.sender.email_address),
                            'subject': item.subject,
                            'received_date': target_date,
                            'source': 'email'
                        })

                        logger.info(f"Fichier téléchargé depuis Exchange: {filename}")

            logger.info(f"Total de fichiers téléchargés depuis Exchange: {len(downloaded_files)}")
            return downloaded_files

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des pièces jointes Exchange: {e}")
            return downloaded_files
