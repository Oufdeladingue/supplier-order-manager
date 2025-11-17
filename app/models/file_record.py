"""
Modèles de données pour l'application
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class FileStatus(Enum):
    """Statuts possibles d'un fichier"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
    MERGED = "merged"


class FileSource(Enum):
    """Sources d'origine des fichiers"""
    EMAIL = "email"
    FTP = "ftp"
    MANUAL = "manual"


class FileType(Enum):
    """Types de fichiers supportés"""
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"


@dataclass
class FileRecord:
    """Représente un fichier de commande fournisseur"""
    id: str
    filename: str
    supplier_code: str
    supplier_name: Optional[str]
    received_date: datetime
    file_type: FileType
    status: FileStatus
    original_path: Optional[str] = None
    transformed_path: Optional[str] = None
    row_count: Optional[int] = None
    file_size: Optional[int] = None
    locked_by: Optional[str] = None
    locked_by_name: Optional[str] = None
    locked_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    processed_by_name: Optional[str] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileRecord':
        """Crée une instance depuis un dictionnaire (réponse Supabase)"""
        # Extraire les informations du fournisseur si disponibles
        supplier_name = None
        if 'suppliers' in data and data['suppliers']:
            supplier_name = data['suppliers'].get('name')

        # Extraire le nom de l'utilisateur qui a verrouillé
        locked_by_name = None
        if 'profiles' in data and isinstance(data.get('locked_by'), str):
            locked_by_name = data['profiles'].get('full_name')

        return cls(
            id=data['id'],
            filename=data['filename'],
            supplier_code=data['supplier_code'],
            supplier_name=supplier_name,
            received_date=datetime.fromisoformat(data['received_date']),
            file_type=FileType(data['file_type']),
            status=FileStatus(data['status']),
            original_path=data.get('original_path'),
            transformed_path=data.get('transformed_path'),
            row_count=data.get('row_count'),
            file_size=data.get('file_size'),
            locked_by=data.get('locked_by'),
            locked_by_name=locked_by_name,
            locked_at=datetime.fromisoformat(data['locked_at']) if data.get('locked_at') else None,
            processed_by=data.get('processed_by'),
            processed_at=datetime.fromisoformat(data['processed_at']) if data.get('processed_at') else None,
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour Supabase"""
        return {
            'id': self.id,
            'filename': self.filename,
            'supplier_code': self.supplier_code,
            'received_date': self.received_date.date().isoformat(),
            'file_type': self.file_type.value,
            'status': self.status.value,
            'original_path': self.original_path,
            'transformed_path': self.transformed_path,
            'row_count': self.row_count,
            'file_size': self.file_size,
            'locked_by': self.locked_by,
            'locked_at': self.locked_at.isoformat() if self.locked_at else None,
            'processed_by': self.processed_by,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'error_message': self.error_message
        }

    @property
    def is_locked(self) -> bool:
        """Vérifie si le fichier est verrouillé"""
        return self.locked_by is not None

    @property
    def can_be_processed(self) -> bool:
        """Vérifie si le fichier peut être traité"""
        return self.status in [FileStatus.PENDING, FileStatus.ERROR] and not self.is_locked


@dataclass
class Supplier:
    """Représente un fournisseur"""
    id: str
    supplier_code: str
    name: str
    email_pattern: Optional[str]
    file_patterns: List[str]
    source: FileSource
    ftp_config: Optional[Dict[str, Any]]
    transformation_rules: Optional[Dict[str, Any]]
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Supplier':
        """Crée une instance depuis un dictionnaire"""
        return cls(
            id=data['id'],
            supplier_code=data['supplier_code'],
            name=data['name'],
            email_pattern=data.get('email_pattern'),
            file_patterns=data.get('file_patterns', []),
            source=FileSource(data['source']),
            ftp_config=data.get('ftp_config'),
            transformation_rules=data.get('transformation_rules'),
            active=data.get('active', True),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class ProcessingHistoryEntry:
    """Représente une entrée d'historique"""
    id: str
    file_id: str
    user_id: str
    user_name: Optional[str]
    action: str
    details: Dict[str, Any]
    created_at: datetime

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingHistoryEntry':
        """Crée une instance depuis un dictionnaire"""
        user_name = None
        if 'profiles' in data and data['profiles']:
            user_name = data['profiles'].get('full_name')

        return cls(
            id=data['id'],
            file_id=data['file_id'],
            user_id=data['user_id'],
            user_name=user_name,
            action=data['action'],
            details=data.get('details', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )
