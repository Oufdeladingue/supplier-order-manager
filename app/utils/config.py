"""
Gestion centralisée de la configuration
Fonctionne à la fois en mode développement (avec .env) et en mode production (exécutable)
"""

import os
from typing import Dict, Any
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

        # FTP - OBLIGATOIRE depuis .env (pas de valeurs par défaut pour sécurité)
        self.FTP_HOST = os.getenv("FTP_HOST")
        self.FTP_PORT = int(os.getenv("FTP_PORT", 22))
        self.FTP_USERNAME = os.getenv("FTP_USERNAME")
        self.FTP_PASSWORD = os.getenv("FTP_PASSWORD")
        self.FTP_PATH = os.getenv("FTP_PATH")

        # Avertir si les identifiants FTP ne sont pas configurés
        if not all([self.FTP_HOST, self.FTP_USERNAME, self.FTP_PASSWORD]):
            logger.warning("⚠️ Identifiants FTP manquants dans .env - Les fonctionnalités FTP seront désactivées")

        logger.info("Configuration chargée avec succès")

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
