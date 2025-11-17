"""
Gestion centralisée de la configuration
Fonctionne à la fois en mode développement (avec .env) et en mode production (exécutable)
Mode production : récupère les identifiants FTP depuis Supabase
"""

import os
from typing import Dict, Any, Optional
from loguru import logger


class Config:
    """Classe singleton pour gérer la configuration de l'application"""

    _instance = None

    # Identifiants Supabase (valeurs par défaut pour mode production)
    # Note: Ces clés sont des clés publiques (anon key) - pas de risque de sécurité
    SUPABASE_URL = "https://iwdvawwspsigddzvvdlu.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3ZHZhd3dzcHNpZ2RkenZ2ZGx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NjU0NjUsImV4cCI6MjA3ODU0MTQ2NX0.CiDsCo-WqhwPgWQkiooSEoXOLvDbp6yXrxJGAe3uJHU"

    # Identifiants FTP - AUCUNE VALEUR PAR DÉFAUT (sensible)
    # Ces valeurs DOIVENT être fournies via .env ou variables d'environnement
    FTP_HOST = None
    FTP_PORT = 22
    FTP_USERNAME = None
    FTP_PASSWORD = None
    FTP_PATH = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._load_config()
            self._initialized = True

    def _load_config(self):
        """
        Charge la configuration depuis les variables d'environnement si disponibles,
        sinon utilise les valeurs par défaut intégrées
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            # Si dotenv n'est pas disponible ou .env n'existe pas, utiliser les valeurs par défaut
            logger.info("Fichier .env non trouvé, utilisation de la configuration intégrée")

        # Supabase - Utiliser .env en priorité, sinon valeurs par défaut
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", self.SUPABASE_URL)
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", self.SUPABASE_KEY)

        # FTP - Priorité 1: .env, Priorité 2: Supabase (chargé plus tard après connexion)
        self.FTP_HOST = os.getenv("FTP_HOST")
        self.FTP_PORT = int(os.getenv("FTP_PORT", 22))
        self.FTP_USERNAME = os.getenv("FTP_USERNAME")
        self.FTP_PASSWORD = os.getenv("FTP_PASSWORD")
        self.FTP_PATH = os.getenv("FTP_PATH")

        # Note: Si les identifiants FTP ne sont pas dans .env, ils seront chargés depuis Supabase
        # lors de l'appel à load_ftp_from_supabase() après la connexion utilisateur

        logger.info("Configuration chargée avec succès")

    def load_ftp_from_supabase(self, supabase_client) -> bool:
        """
        Charge les identifiants FTP depuis Supabase si non présents dans .env

        Args:
            supabase_client: Instance du client Supabase authentifié

        Returns:
            bool: True si les identifiants ont été chargés, False sinon
        """
        # Si les identifiants FTP sont déjà présents (via .env), ne pas les remplacer
        if all([self.FTP_HOST, self.FTP_USERNAME, self.FTP_PASSWORD]):
            logger.info("Identifiants FTP déjà configurés via .env")
            return True

        try:
            # Récupérer les paramètres de l'organisation depuis Supabase
            response = supabase_client.client.table('organization_settings')\
                .select('ftp_host, ftp_port, ftp_username, ftp_password, ftp_path')\
                .eq('organization_name', 'default')\
                .execute()

            if response.data and len(response.data) > 0:
                org_settings = response.data[0]

                # Charger les identifiants FTP depuis Supabase
                self.FTP_HOST = org_settings.get('ftp_host')
                self.FTP_PORT = org_settings.get('ftp_port', 22)
                self.FTP_USERNAME = org_settings.get('ftp_username')
                self.FTP_PASSWORD = org_settings.get('ftp_password')
                self.FTP_PATH = org_settings.get('ftp_path')

                if all([self.FTP_HOST, self.FTP_USERNAME, self.FTP_PASSWORD]):
                    logger.info("✅ Identifiants FTP chargés depuis Supabase")
                    return True
                else:
                    logger.warning("⚠️ Identifiants FTP incomplets dans Supabase")
                    return False
            else:
                logger.warning("⚠️ Aucun paramètre d'organisation trouvé dans Supabase")
                return False

        except Exception as e:
            logger.error(f"Erreur lors du chargement des identifiants FTP depuis Supabase: {e}")
            return False

    def get_supabase_config(self) -> Dict[str, str]:
        """Retourne la configuration Supabase"""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_KEY
        }

    def get_ftp_config(self) -> Dict[str, Any]:
        """Retourne la configuration FTP"""
        return {
            "host": self.FTP_HOST,
            "port": self.FTP_PORT,
            "username": self.FTP_USERNAME,
            "password": self.FTP_PASSWORD,
            "path": self.FTP_PATH
        }


# Instance globale
config = Config()
