"""
Point d'entrée principal de l'application
Gestionnaire de Commandes Fournisseurs
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Version de l'application
__version__ = "1.0.2"

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from app.ui.main_window import MainWindow
from app.utils import get_resource_path

# Configuration du logger
log_folder = Path("logs")
log_folder.mkdir(exist_ok=True)
logger.add("logs/app_{time}.log", rotation="1 day", retention="30 days", level="DEBUG")


def main():
    """Lance l'application"""
    logger.info("=" * 60)
    logger.info("Démarrage de l'application Gestionnaire Commandes Fournisseurs")
    logger.info("=" * 60)

    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName(os.getenv("APP_NAME", "Gestionnaire Commandes Fournisseurs"))
    app.setApplicationVersion(__version__)

    # Définir l'icône de l'application
    icon_path = get_resource_path("assets/logo/logo.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        logger.info(f"Icône de l'application chargée: {icon_path}")
    else:
        logger.warning(f"Icône de l'application introuvable: {icon_path}")

    # Créer et afficher la fenêtre immédiatement avec le loader interne
    window = MainWindow()
    window.show()

    # Utiliser QTimer pour démarrer le chargement après que la boucle d'événements soit lancée
    # Cela permet au spinner d'être visible et animé pendant le chargement
    from PySide6.QtCore import QTimer
    QTimer.singleShot(100, window.start_initial_load)  # Démarrage après 100ms

    # Lancer la boucle d'événements
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
