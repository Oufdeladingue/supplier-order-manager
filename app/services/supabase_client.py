"""
Client Supabase pour l'application de gestion des commandes fournisseurs.
Gère les connexions, l'authentification et les opérations CRUD.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from supabase import create_client, Client
from loguru import logger

from app.utils import config


class SupabaseClient:
    """Client singleton pour gérer les interactions avec Supabase"""

    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    _current_user: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._initialize_client()

    def _initialize_client(self):
        """Initialise la connexion à Supabase"""
        # Récupérer la configuration depuis le singleton
        supabase_config = config.get_supabase_config()
        url = supabase_config["url"]
        key = supabase_config["key"]

        if not url or not key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être définis")

        try:
            self._client = create_client(url, key)
            logger.info("Connexion à Supabase établie")
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Supabase: {e}")
            raise

    @property
    def client(self) -> Client:
        """Retourne le client Supabase"""
        if self._client is None:
            self._initialize_client()
        return self._client

    # ==================== AUTHENTIFICATION ====================

    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Connexion d'un utilisateur"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self._current_user = response.user
            logger.info(f"Utilisateur connecté: {email}")
            return {"success": True, "user": response.user}
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
            return {"success": False, "error": str(e)}

    def sign_out(self) -> bool:
        """Déconnexion de l'utilisateur"""
        try:
            self.client.auth.sign_out()
            self._current_user = None
            logger.info("Utilisateur déconnecté")
            return True
        except Exception as e:
            logger.error(f"Erreur de déconnexion: {e}")
            return False

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Retourne l'utilisateur actuellement connecté"""
        try:
            user = self.client.auth.get_user()
            return user.user if user else None
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return None

    # ==================== FICHIERS ====================

    def get_files(self, status: Optional[str] = None,
                  supplier_code: Optional[str] = None,
                  date_from: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Récupère la liste des fichiers avec filtres optionnels"""
        try:
            query = self.client.table('files').select('*, suppliers(*), profiles(full_name, email)')

            if status:
                query = query.eq('status', status)
            if supplier_code:
                query = query.eq('supplier_code', supplier_code)
            if date_from:
                query = query.gte('received_date', date_from.isoformat())

            query = query.order('received_date', desc=True).order('created_at', desc=True)

            response = query.execute()
            logger.debug(f"Fichiers récupérés: {len(response.data)}")
            return response.data
        except Exception as e:
            logger.error(f"Erreur récupération fichiers: {e}")
            return []

    def create_file(self, file_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un nouvel enregistrement de fichier"""
        try:
            response = self.client.table('files').insert(file_data).execute()
            logger.info(f"Fichier créé: {file_data.get('filename')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erreur création fichier: {e}")
            return None

    def update_file(self, file_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un fichier"""
        try:
            self.client.table('files').update(updates).eq('id', file_id).execute()
            logger.info(f"Fichier mis à jour: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur mise à jour fichier: {e}")
            return False

    def lock_file(self, file_id: str, user_id: str) -> bool:
        """Verrouille un fichier pour traitement"""
        try:
            # Vérifier si le fichier n'est pas déjà verrouillé
            file = self.client.table('files').select('locked_by').eq('id', file_id).execute()

            if file.data and file.data[0].get('locked_by'):
                logger.warning(f"Fichier déjà verrouillé: {file_id}")
                return False

            updates = {
                'locked_by': user_id,
                'locked_at': datetime.utcnow().isoformat(),
                'status': 'processing'
            }

            self.client.table('files').update(updates).eq('id', file_id).execute()

            # Ajouter une entrée dans l'historique
            self.add_history_entry(file_id, user_id, 'locked', {'timestamp': datetime.utcnow().isoformat()})

            logger.info(f"Fichier verrouillé: {file_id} par {user_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur verrouillage fichier: {e}")
            return False

    def unlock_file(self, file_id: str, user_id: str, new_status: str = 'pending') -> bool:
        """Déverrouille un fichier"""
        try:
            updates = {
                'locked_by': None,
                'locked_at': None,
                'status': new_status
            }

            self.client.table('files').update(updates).eq('id', file_id).execute()

            # Ajouter une entrée dans l'historique
            self.add_history_entry(file_id, user_id, 'unlocked', {'timestamp': datetime.utcnow().isoformat()})

            logger.info(f"Fichier déverrouillé: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur déverrouillage fichier: {e}")
            return False

    # ==================== FOURNISSEURS ====================

    def get_suppliers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Récupère la liste des fournisseurs"""
        try:
            query = self.client.table('suppliers').select('*')

            if active_only:
                query = query.eq('active', True)

            response = query.execute()
            logger.debug(f"Fournisseurs récupérés: {len(response.data)}")
            return response.data
        except Exception as e:
            logger.error(f"Erreur récupération fournisseurs: {e}")
            return []

    def get_supplier_by_code(self, supplier_code: str) -> Optional[Dict[str, Any]]:
        """Récupère un fournisseur par son code"""
        try:
            response = self.client.table('suppliers').select('*').eq('supplier_code', supplier_code).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Erreur récupération fournisseur: {e}")
            return None

    # ==================== HISTORIQUE ====================

    def add_history_entry(self, file_id: str, user_id: str, action: str, details: Dict[str, Any]) -> bool:
        """Ajoute une entrée dans l'historique"""
        try:
            entry = {
                'file_id': file_id,
                'user_id': user_id,
                'action': action,
                'details': details
            }
            self.client.table('processing_history').insert(entry).execute()
            logger.debug(f"Historique ajouté: {action} pour fichier {file_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout historique: {e}")
            return False

    def get_file_history(self, file_id: str) -> List[Dict[str, Any]]:
        """Récupère l'historique d'un fichier"""
        try:
            response = self.client.table('processing_history')\
                .select('*, profiles(full_name, email)')\
                .eq('file_id', file_id)\
                .order('created_at', desc=True)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return []

    # ==================== STORAGE ====================

    def upload_file(self, bucket: str, file_path: str, file_content: bytes) -> Optional[str]:
        """Upload un fichier vers Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).upload(file_path, file_content)
            logger.info(f"Fichier uploadé: {file_path} dans {bucket}")
            return file_path
        except Exception as e:
            logger.error(f"Erreur upload fichier: {e}")
            return None

    def download_file(self, bucket: str, file_path: str) -> Optional[bytes]:
        """Télécharge un fichier depuis Supabase Storage"""
        try:
            response = self.client.storage.from_(bucket).download(file_path)
            logger.info(f"Fichier téléchargé: {file_path} depuis {bucket}")
            return response
        except Exception as e:
            logger.error(f"Erreur téléchargement fichier: {e}")
            return None

    def get_public_url(self, bucket: str, file_path: str) -> Optional[str]:
        """Génère une URL publique pour un fichier"""
        try:
            response = self.client.storage.from_(bucket).get_public_url(file_path)
            return response
        except Exception as e:
            logger.error(f"Erreur génération URL: {e}")
            return None

    # ==================== REALTIME ====================

    def subscribe_to_files(self, callback):
        """S'abonne aux changements en temps réel sur la table files"""
        try:
            channel = self.client.channel('files-channel')
            channel.on_postgres_changes(
                event='*',
                schema='public',
                table='files',
                callback=callback
            ).subscribe()
            logger.info("Abonnement realtime activé pour les fichiers")
            return channel
        except Exception as e:
            logger.error(f"Erreur abonnement realtime: {e}")
            return None


# Instance globale
supabase_client = SupabaseClient()
