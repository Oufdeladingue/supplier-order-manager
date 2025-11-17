"""
Service pour automatiser la connexion aux sites web des fournisseurs
"""

import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
import undetected_chromedriver as uc
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService


class WebAutomationService:
    """Service pour automatiser la connexion aux sites web des fournisseurs"""

    def __init__(self, browser_type: str = 'chrome'):
        """
        Initialise le service d'automatisation web

        Args:
            browser_type: Type de navigateur ('chrome', 'firefox', 'edge')
        """
        self.browser_type = browser_type.lower()
        self.driver: Optional[webdriver.Remote] = None
        self.wait_timeout = 10  # Secondes

    @staticmethod
    def _is_chrome_installed() -> bool:
        """Vérifie si Chrome est installé"""
        import platform
        import subprocess

        if platform.system() == 'Windows':
            try:
                # Vérifier si chrome.exe existe dans les emplacements standards
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        return True
                return False
            except:
                return False
        return True  # Sur Linux/Mac, on suppose que c'est géré par le système

    def _get_driver(self) -> webdriver.Remote:
        """
        Crée et configure le driver Selenium approprié avec options anti-détection

        Returns:
            WebDriver configuré
        """
        try:
            if self.browser_type == 'firefox':
                service = FirefoxService(GeckoDriverManager().install())
                options = webdriver.FirefoxOptions()

                # Anti-détection pour Firefox
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference('useAutomationExtension', False)
                options.set_preference("general.useragent.override",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")

                driver = webdriver.Firefox(service=service, options=options)

            elif self.browser_type == 'edge':
                service = EdgeService(EdgeChromiumDriverManager().install())
                options = webdriver.EdgeOptions()

                # Anti-détection pour Edge
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-gpu')
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")

                driver = webdriver.Edge(service=service, options=options)

            else:  # Chrome par défaut
                # Vérifier si Chrome est installé, sinon utiliser Edge
                chrome_installed = self._is_chrome_installed()

                if not chrome_installed:
                    logger.warning("Chrome n'est pas installé, utilisation de Edge comme fallback")
                    # Rediriger vers Edge
                    service = EdgeService(EdgeChromiumDriverManager().install())
                    options = webdriver.EdgeOptions()

                    # Profil dédié pour Edge
                    app_data_dir = Path.home() / '.supplier_order_manager' / 'edge_profile'
                    app_data_dir.mkdir(parents=True, exist_ok=True)
                    options.add_argument(f'--user-data-dir={str(app_data_dir)}')

                    # Anti-détection pour Edge
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-gpu')
                    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")

                    # Préférences
                    prefs = {
                        "credentials_enable_service": False,
                        "profile.password_manager_enabled": False,
                        "profile.default_content_setting_values.notifications": 2
                    }
                    options.add_experimental_option("prefs", prefs)

                    driver = webdriver.Edge(service=service, options=options)
                    logger.info("Driver Edge initialisé avec succès (fallback - Chrome non installé)")

                else:
                    # Créer un profil Chrome dédié à l'application
                    # Cela simule un utilisateur réel qui revient régulièrement
                    app_data_dir = Path.home() / '.supplier_order_manager' / 'chrome_profile'
                    app_data_dir.mkdir(parents=True, exist_ok=True)

                    logger.info(f"Utilisation du profil Chrome dédié: {app_data_dir}")

                    # Détecter si on est dans un exécutable PyInstaller
                    import sys
                    is_frozen = getattr(sys, 'frozen', False)

                    if is_frozen:
                        # Mode PyInstaller : utiliser webdriver standard pour éviter les subprocess
                        logger.info("Mode PyInstaller détecté : utilisation de webdriver standard")
                        from selenium.webdriver.chrome.service import Service as ChromeService
                        from webdriver_manager.chrome import ChromeDriverManager

                        options = webdriver.ChromeOptions()

                        # Utiliser le profil dédié
                        options.add_argument(f'--user-data-dir={str(app_data_dir)}')

                        # Anti-détection (maximum possible sans undetected-chromedriver)
                        options.add_argument('--disable-blink-features=AutomationControlled')
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                        options.add_argument('--disable-dev-shm-usage')
                        options.add_argument('--no-sandbox')
                        options.add_argument('--disable-gpu')
                        options.add_argument('--start-maximized')

                        # User agent réaliste
                        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

                        # Préférences pour désactiver les popups
                        prefs = {
                            "credentials_enable_service": False,
                            "profile.password_manager_enabled": False,
                            "profile.default_content_setting_values.notifications": 2
                        }
                        options.add_experimental_option("prefs", prefs)

                        # Créer le service avec flags de détachement
                        service = ChromeService(ChromeDriverManager().install())

                        # Créer le driver
                        driver = webdriver.Chrome(service=service, options=options)

                else:
                    # Mode développement : utiliser undetected-chromedriver
                    logger.info("Mode développement : utilisation de undetected-chromedriver")
                    options = uc.ChromeOptions()

                    # Utiliser le profil dédié
                    options.add_argument(f'--user-data-dir={str(app_data_dir)}')

                    # Options minimales (undetected-chromedriver gère déjà la plupart)
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--no-sandbox')

                    # Préférences pour désactiver les popups
                    prefs = {
                        "credentials_enable_service": False,
                        "profile.password_manager_enabled": False,
                        "profile.default_content_setting_values.notifications": 2
                    }
                    options.add_experimental_option("prefs", prefs)

                    # Créer le driver avec undetected-chromedriver
                    driver = uc.Chrome(
                        options=options,
                        version_main=None,
                        use_subprocess=False
                    )

            # Configuration commune
            driver.maximize_window()

            # Indiquer le type de driver utilisé
            if self.browser_type == 'chrome':
                logger.info(f"Driver Chrome initialisé avec succès (undetected-chromedriver - anti-bot)")
            else:
                logger.info(f"Driver {self.browser_type} initialisé avec succès (mode anti-détection)")

            return driver

        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du driver {self.browser_type}: {e}")
            raise

    def _find_element_by_selector(self, selector: str, wait: bool = True) -> Optional[Any]:
        """
        Trouve un élément par son sélecteur (CSS, XPath, name, id, etc.)

        Args:
            selector: Sélecteur de l'élément
            wait: Si True, attend que l'élément soit présent

        Returns:
            Élément trouvé ou None
        """
        if not selector or not self.driver:
            return None

        try:
            # Déterminer le type de sélecteur
            by_type = By.CSS_SELECTOR

            # XPath
            if selector.startswith('//') or selector.startswith('(//'):
                by_type = By.XPATH
            # ID
            elif selector.startswith('#') and ' ' not in selector:
                selector = selector[1:]
                by_type = By.ID
            # Name
            elif selector.startswith('[name='):
                # Extraire la valeur du name
                selector = selector.split('"')[1] if '"' in selector else selector.split("'")[1]
                by_type = By.NAME
            # Class
            elif selector.startswith('.') and ' ' not in selector:
                selector = selector[1:]
                by_type = By.CLASS_NAME

            # Attendre que l'élément soit présent
            if wait:
                element = WebDriverWait(self.driver, self.wait_timeout).until(
                    EC.presence_of_element_located((by_type, selector))
                )
            else:
                element = self.driver.find_element(by_type, selector)

            return element

        except TimeoutException:
            logger.warning(f"Timeout: élément non trouvé avec le sélecteur '{selector}'")
            return None
        except NoSuchElementException:
            logger.warning(f"Élément non trouvé avec le sélecteur '{selector}'")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'élément '{selector}': {e}")
            return None

    def _human_delay(self, min_sec: float = 0.5, max_sec: float = 1.5):
        """Attend un délai aléatoire pour simuler un comportement humain"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _type_like_human(self, element, text: str):
        """Tape du texte avec des délais aléatoires entre chaque caractère"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # 50-150ms entre chaque caractère

    def auto_login(self, web_config: Dict[str, Any]) -> bool:
        """
        Effectue la connexion automatique au site du fournisseur

        Args:
            web_config: Configuration de connexion web (depuis la table suppliers)

        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        try:
            # Vérifier que l'URL est présente
            url = web_config.get('url', '')
            if not url:
                logger.error("URL manquante dans la configuration")
                return False

            # Créer le driver
            self.driver = self._get_driver()

            logger.info(f"Navigation vers {url}")
            self.driver.get(url)

            # Attendre que la page charge (délai humain)
            self._human_delay(2, 3)

            # 5. Gérer le cookie d'abord si activé (avant de remplir les champs)
            if web_config.get('cookie_enabled', False):
                cookie_selector = web_config.get('cookie_selector', '')
                if cookie_selector:
                    logger.info("Clic sur le bouton de validation des cookies")
                    element = self._find_element_by_selector(cookie_selector)
                    if element:
                        element.click()
                        self._human_delay(1, 2)
                    else:
                        logger.warning("Bouton cookie non trouvé")

            # 1. Remplir le code client si activé
            if web_config.get('client_code_enabled', False):
                client_code_value = web_config.get('client_code_value', '')
                client_code_selector = web_config.get('client_code_selector', '')

                if client_code_value and client_code_selector:
                    logger.info("Remplissage du code client")
                    element = self._find_element_by_selector(client_code_selector)
                    if element:
                        self._type_like_human(element, client_code_value)
                        self._human_delay(0.5, 1)
                    else:
                        logger.warning("Champ code client non trouvé")

                # 1.1. Gérer l'étape intermédiaire juste après le code client si activée
                if web_config.get('intermediate_enabled', False):
                    intermediate_selector = web_config.get('intermediate_selector', '')
                    if intermediate_selector:
                        logger.info("Clic sur le bouton intermédiaire (après code client)")
                        element = self._find_element_by_selector(intermediate_selector)
                        if element:
                            element.click()
                            self._human_delay(2, 3)
                        else:
                            logger.warning("Bouton intermédiaire non trouvé")

            # 2. Remplir le login
            login_value = web_config.get('login_value', '')
            login_selector = web_config.get('login_selector', '')

            if login_value and login_selector:
                logger.info("Remplissage du login")
                element = self._find_element_by_selector(login_selector)
                if element:
                    self._type_like_human(element, login_value)
                    self._human_delay(0.5, 1)
                else:
                    logger.warning("Champ login non trouvé")

            # 3. Remplir le mot de passe
            password_value = web_config.get('password_value', '')
            password_selector = web_config.get('password_selector', '')

            if password_value and password_selector:
                logger.info("Remplissage du mot de passe")
                element = self._find_element_by_selector(password_selector)
                if element:
                    self._type_like_human(element, password_value)
                    self._human_delay(0.5, 1)
                else:
                    logger.warning("Champ mot de passe non trouvé")

            # 4. Remplir l'autre champ si activé
            if web_config.get('other_enabled', False):
                other_value = web_config.get('other_value', '')
                other_selector = web_config.get('other_selector', '')

                if other_value and other_selector:
                    logger.info("Remplissage du champ supplémentaire")
                    element = self._find_element_by_selector(other_selector)
                    if element:
                        self._type_like_human(element, other_value)
                        self._human_delay(0.5, 1)
                    else:
                        logger.warning("Champ supplémentaire non trouvé")

            # 6. Cliquer sur le bouton de validation
            submit_selector = web_config.get('submit_selector', '')
            if submit_selector:
                logger.info("Clic sur le bouton de validation")
                self._human_delay(0.5, 1)  # Délai avant de cliquer
                element = self._find_element_by_selector(submit_selector)
                if element:
                    element.click()
                    self._human_delay(2, 3)
                else:
                    logger.warning("Bouton de validation non trouvé")

            # 7. Détecter le CAPTCHA si activé
            if web_config.get('captcha_detect', False):
                logger.info("⚠️ CAPTCHA détecté dans la configuration")
                logger.info("Veuillez résoudre le CAPTCHA manuellement dans le navigateur")
                # Le navigateur reste ouvert pour que l'utilisateur puisse résoudre le CAPTCHA
                # et continuer manuellement

            logger.success("Connexion automatique terminée avec succès!")
            logger.info("Le navigateur reste ouvert pour que vous puissiez continuer")
            return True

        except WebDriverException as e:
            logger.error(f"Erreur WebDriver: {e}")
            self.close()
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la connexion automatique: {e}")
            import traceback
            traceback.print_exc()
            self.close()
            return False

    def close(self):
        """Ferme le driver et libère les ressources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fermé")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture du driver: {e}")
            finally:
                self.driver = None


def auto_login_supplier(web_config: Dict[str, Any], browser_type: str = 'chrome') -> bool:
    """
    Fonction helper pour effectuer une connexion automatique

    Args:
        web_config: Configuration de connexion web
        browser_type: Type de navigateur à utiliser

    Returns:
        bool: True si la connexion a réussi, False sinon
    """
    service = WebAutomationService(browser_type=browser_type)
    try:
        return service.auto_login(web_config)
    except Exception as e:
        logger.error(f"Erreur lors de la connexion automatique: {e}")
        return False
    # Note: on ne ferme pas le driver pour laisser l'utilisateur continuer
