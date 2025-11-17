"""
Écran de chargement (splash screen) pour l'application
"""

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont


class LoadingSpinner(QWidget):
    """Widget de spinner de chargement animé"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(80, 80)

        # Timer pour l'animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # Mise à jour toutes les 50ms

    def rotate(self):
        """Fait tourner le spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        """Dessine le spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Centre du widget
        center_x = self.width() / 2
        center_y = self.height() / 2

        # Dessiner le cercle de chargement
        painter.setPen(Qt.NoPen)

        # 12 points pour le spinner
        import math
        for i in range(12):
            # Calculer l'opacité en fonction de la position
            angle_offset = (self.angle + i * 30) % 360
            opacity = 1.0 - (i / 12.0)

            # Couleur avec opacité
            color = QColor("#2196F3")
            color.setAlphaF(opacity)
            painter.setBrush(color)

            # Position du point (cercle de rayon 25px)
            angle_rad = math.radians(angle_offset)
            x = center_x + 25 * math.cos(angle_rad)
            y = center_y + 25 * math.sin(angle_rad)

            # Dessiner un petit cercle
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)


class SplashScreen(QSplashScreen):
    """Écran de chargement personnalisé"""

    def __init__(self):
        # Créer un pixmap transparent
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.transparent)

        super().__init__(pixmap)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Widget central
        container = QWidget(self)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #2196F3;
            }
        """)
        container.setGeometry(0, 0, 500, 300)

        # Layout
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Titre
        title = QLabel("M-Jardin")
        title.setStyleSheet("""
            QLabel {
                font-size: 32pt;
                font-weight: bold;
                color: #2196F3;
                background: transparent;
                border: none;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Spinner
        self.spinner = LoadingSpinner()
        spinner_container = QWidget()
        spinner_layout = QVBoxLayout(spinner_container)
        spinner_layout.setAlignment(Qt.AlignCenter)
        spinner_layout.addWidget(self.spinner)
        spinner_container.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(spinner_container)

        # Message de chargement
        self.message = QLabel("Chargement de l'assistant de commande M-Jardin")
        self.message.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #666;
                background: transparent;
                border: none;
            }
        """)
        self.message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message)

        # Version
        version = QLabel("v1.0.0")
        version.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #999;
                background: transparent;
                border: none;
            }
        """)
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

    def set_message(self, message: str):
        """Change le message de chargement"""
        self.message.setText(message)
        self.repaint()
