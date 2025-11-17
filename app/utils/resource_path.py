"""
Utilitaire pour obtenir le chemin correct des ressources
Fonctionne à la fois en mode développement et en mode exécutable compilé
"""

import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Obtient le chemin absolu vers une ressource

    Fonctionne correctement que l'application soit exécutée:
    - En mode développement (python app/main.py)
    - En mode exécutable compilé (PyInstaller)

    Args:
        relative_path: Chemin relatif depuis la racine du projet (ex: "assets/logo/logo.png")

    Returns:
        Path: Chemin absolu vers la ressource

    Example:
        >>> logo_path = get_resource_path("assets/logo/logo.png")
        >>> icon_path = get_resource_path("assets/icons/refresh.svg")
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # En mode développement, utiliser le dossier parent du dossier app
        base_path = Path(__file__).parent.parent.parent

    return base_path / relative_path
