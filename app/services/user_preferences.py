"""
Service pour gérer les préférences utilisateur locales (spécifiques au poste)
"""

import json
import subprocess
import webbrowser
from pathlib import Path
from loguru import logger


def get_output_folder() -> Path:
    """
    Récupère le dossier de sortie configuré par l'utilisateur

    Returns:
        Path: Le chemin du dossier de sortie (par défaut: Downloads)
    """
    try:
        config_file = Path.home() / '.supplier_order_manager' / 'workstation_config.json'

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                local_settings = json.load(f)

            output_folder = local_settings.get('output_folder')
            if output_folder:
                folder_path = Path(output_folder)
                # Créer le dossier s'il n'existe pas
                folder_path.mkdir(parents=True, exist_ok=True)
                return folder_path

    except Exception as e:
        logger.error(f"Erreur lors de la lecture des préférences utilisateur: {e}")

    # Valeur par défaut: dossier Téléchargements
    default_folder = Path.home() / "Downloads"
    default_folder.mkdir(parents=True, exist_ok=True)
    return default_folder


def save_output_folder(folder_path: str) -> bool:
    """
    Sauvegarde le dossier de sortie dans les préférences utilisateur

    Args:
        folder_path: Chemin du dossier de sortie

    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    try:
        config_dir = Path.home() / '.supplier_order_manager'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'workstation_config.json'

        # Lire les préférences existantes
        local_settings = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                local_settings = json.load(f)

        # Mettre à jour le dossier de sortie
        local_settings['output_folder'] = str(folder_path)

        # Sauvegarder
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(local_settings, f, indent=2, ensure_ascii=False)

        logger.info(f"Dossier de sortie sauvegardé: {folder_path}")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du dossier de sortie: {e}")
        return False


def get_browser_config() -> dict:
    """
    Récupère la configuration du navigateur

    Returns:
        dict: Configuration avec 'browser' et 'custom_browser_path'
    """
    try:
        config_file = Path.home() / '.supplier_order_manager' / 'workstation_config.json'

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                local_settings = json.load(f)

            return {
                'browser': local_settings.get('browser', 'Navigateur par défaut du système'),
                'custom_browser_path': local_settings.get('custom_browser_path', '')
            }

    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la configuration du navigateur: {e}")

    # Valeur par défaut
    return {
        'browser': 'Navigateur par défaut du système',
        'custom_browser_path': ''
    }


def get_refresh_interval() -> int:
    """
    Récupère l'intervalle de rafraîchissement automatique configuré (en secondes)

    Returns:
        int: Intervalle en secondes (0 = désactivé)
    """
    try:
        config_file = Path.home() / '.supplier_order_manager' / 'workstation_config.json'

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                local_settings = json.load(f)

            return local_settings.get('refresh_interval', 0)

    except Exception as e:
        logger.error(f"Erreur lors de la lecture de l'intervalle de rafraîchissement: {e}")

    # Valeur par défaut: désactivé
    return 0


def open_url(url: str) -> bool:
    """
    Ouvre une URL avec le navigateur configuré

    Args:
        url: URL à ouvrir

    Returns:
        bool: True si l'ouverture a réussi, False sinon
    """
    try:
        config = get_browser_config()
        browser_choice = config['browser']

        # Chemins des navigateurs courants sur Windows
        browser_paths = {
            'Google Chrome': [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
            ],
            'Mozilla Firefox': [
                r'C:\Program Files\Mozilla Firefox\firefox.exe',
                r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
            ],
            'Microsoft Edge': [
                r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
            ],
            'Opera': [
                r'C:\Program Files\Opera\launcher.exe',
                r'C:\Users\{username}\AppData\Local\Programs\Opera\launcher.exe'
            ],
            'Brave': [
                r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                r'C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe'
            ]
        }

        if browser_choice == 'Navigateur par défaut du système':
            # Utiliser webbrowser.open() qui réutilise l'instance existante du navigateur
            # et ouvre un nouvel onglet dans la session courante
            # new=2 force l'ouverture dans un nouvel onglet si possible
            webbrowser.open(url, new=2)
            logger.info(f"URL ouverte dans un nouvel onglet du navigateur: {url}")
            return True

        elif browser_choice == 'Personnalisé...':
            # Utiliser le chemin personnalisé
            custom_path = config['custom_browser_path']
            if custom_path and Path(custom_path).exists():
                subprocess.Popen([custom_path, url])
                logger.info(f"URL ouverte avec le navigateur personnalisé {custom_path}: {url}")
                return True
            else:
                logger.error(f"Navigateur personnalisé introuvable: {custom_path}")
                # Fallback sur le navigateur par défaut
                webbrowser.open(url)
                return True

        elif browser_choice in browser_paths:
            # Chercher le navigateur dans les chemins connus
            for browser_path in browser_paths[browser_choice]:
                # Remplacer {username} par le nom d'utilisateur réel
                browser_path = browser_path.replace('{username}', Path.home().name)

                if Path(browser_path).exists():
                    subprocess.Popen([browser_path, url])
                    logger.info(f"URL ouverte avec {browser_choice}: {url}")
                    return True

            # Si le navigateur n'est pas trouvé, utiliser le navigateur par défaut
            logger.warning(f"{browser_choice} introuvable, utilisation du navigateur par défaut")
            webbrowser.open(url)
            return True

        else:
            # Par défaut, utiliser le navigateur système
            webbrowser.open(url)
            return True

    except Exception as e:
        logger.error(f"Erreur lors de l'ouverture de l'URL {url}: {e}")
        # Dernière tentative avec le navigateur par défaut
        try:
            webbrowser.open(url)
            return True
        except:
            return False
