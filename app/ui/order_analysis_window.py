"""
Fenêtre d'analyse des commandes fournisseurs
Permet de visualiser les fichiers du jour, filtrer par fournisseur et voir les statistiques
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, date
from loguru import logger

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QIcon, QColor

import paramiko
import pandas as pd
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent.parent))

load_dotenv()


class FileAnalyzer(QThread):
    """Thread pour analyser les fichiers en arrière-plan"""

    finished = Signal(dict)  # {filename: {rows: int, total: float, data: DataFrame}}
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, files_to_analyze: List[str], ftp_path: str):
        super().__init__()
        self.files_to_analyze = files_to_analyze
        self.ftp_path = ftp_path

    def run(self):
        """Télécharge et analyse les fichiers"""
        try:
            # Connexion SFTP
            host = os.getenv("FTP_HOST")
            port = int(os.getenv("FTP_PORT", 22))
            username = os.getenv("FTP_USERNAME")
            password = os.getenv("FTP_PASSWORD")

            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            results = {}

            for filename in self.files_to_analyze:
                try:
                    self.progress.emit(f"Analyse de {filename}...")

                    # Télécharger le fichier temporairement
                    remote_path = f"{self.ftp_path}/{filename}".replace('//', '/')
                    local_path = f"./temp/{filename}"

                    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                    sftp.get(remote_path, local_path)

                    # Lire le fichier avec pandas
                    # Essayer différents séparateurs et encodages
                    df = None
                    for sep in [';', ',', '\t']:
                        for encoding in ['utf-8', 'latin1', 'cp1252']:
                            try:
                                df = pd.read_csv(local_path, sep=sep, encoding=encoding)
                                if len(df.columns) > 1:  # Vérifier qu'on a bien des colonnes
                                    break
                            except:
                                continue
                        if df is not None and len(df.columns) > 1:
                            break

                    if df is None or len(df.columns) <= 1:
                        self.error.emit(f"Impossible de lire {filename}")
                        continue

                    # Analyser le fichier
                    nb_rows = len(df)

                    # Chercher la colonne de prix (colonne D = index 3, ou chercher "prix", "price", "montant")
                    price_col = None
                    if len(df.columns) > 3:
                        price_col = df.columns[3]  # Colonne D
                    else:
                        # Chercher par nom
                        for col in df.columns:
                            col_lower = str(col).lower()
                            if any(keyword in col_lower for keyword in ['prix', 'price', 'montant', 'total', 'ht']):
                                price_col = col
                                break

                    total_price = 0.0
                    if price_col is not None:
                        try:
                            # Nettoyer et convertir les prix
                            df[price_col] = df[price_col].astype(str).str.replace(',', '.').str.replace(' ', '')
                            df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
                            total_price = df[price_col].sum()
                        except:
                            pass

                    results[filename] = {
                        'rows': nb_rows,
                        'total': total_price,
                        'price_col': price_col,
                        'columns': list(df.columns),
                        'data': df.head(100)  # Garder les 100 premières lignes
                    }

                    # Nettoyer le fichier temporaire
                    Path(local_path).unlink(missing_ok=True)

                except Exception as e:
                    logger.error(f"Erreur analyse {filename}: {e}")
                    self.error.emit(f"Erreur {filename}: {str(e)}")

            sftp.close()
            transport.close()

            self.finished.emit(results)

        except Exception as e:
            logger.error(f"Erreur analyse fichiers: {e}")
            self.error.emit(str(e))


class OrderAnalysisWindow(QMainWindow):
    """Fenêtre d'analyse des commandes"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.files_list = []
        self.suppliers_config = []
        self.selected_supplier = None
        self.analysis_results = {}

        self.init_ui()
        self.load_suppliers_config()
        self.load_today_files()

    def init_ui(self):
        """Initialise l'interface"""
        self.setWindowTitle("Analyse des Commandes Fournisseurs")
        self.setGeometry(100, 100, 1600, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Panneau de gauche : Filtres fournisseurs
        left_panel = self.create_suppliers_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Panneau central : Liste des fichiers
        center_panel = self.create_files_panel()
        main_layout.addWidget(center_panel, stretch=2)

        # Panneau de droite : Statistiques
        right_panel = self.create_stats_panel()
        main_layout.addWidget(right_panel, stretch=1)

    def create_suppliers_panel(self) -> QWidget:
        """Crée le panneau des fournisseurs"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Titre
        title = QLabel("Filtrer par Fournisseur")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Bouton "Tous"
        all_btn = QPushButton("📋 Tous les fournisseurs")
        all_btn.setCheckable(True)
        all_btn.setChecked(True)
        all_btn.clicked.connect(lambda: self.filter_by_supplier(None))
        all_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
                border-color: #4CAF50;
            }
        """)
        layout.addWidget(all_btn)
        self.all_suppliers_btn = all_btn

        # Zone défilante pour les boutons fournisseurs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        self.suppliers_layout = QVBoxLayout(scroll_widget)
        self.suppliers_layout.setSpacing(5)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Bouton rafraîchir
        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.load_today_files)
        layout.addWidget(refresh_btn)

        return widget

    def create_files_panel(self) -> QWidget:
        """Crée le panneau de liste des fichiers"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # En-tête
        header_layout = QHBoxLayout()

        title = QLabel("Fichiers du Jour")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title)

        self.files_count_label = QLabel("0 fichier(s)")
        self.files_count_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self.files_count_label)

        header_layout.addStretch()

        self.analyze_btn = QPushButton("🔍 Analyser les fichiers")
        self.analyze_btn.clicked.connect(self.analyze_selected_files)
        header_layout.addWidget(self.analyze_btn)

        layout.addLayout(header_layout)

        # Table des fichiers
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels([
            "Fichier", "Fournisseur", "Date", "Taille", "Analysé"
        ])
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.files_table.setAlternatingRowColors(True)
        self.files_table.setColumnWidth(0, 300)
        self.files_table.setColumnWidth(1, 150)
        self.files_table.setColumnWidth(2, 100)
        self.files_table.setColumnWidth(3, 80)
        self.files_table.setColumnWidth(4, 80)
        layout.addWidget(self.files_table)

        return widget

    def create_stats_panel(self) -> QWidget:
        """Crée le panneau de statistiques"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Titre
        title = QLabel("Statistiques")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Groupe statistiques globales
        stats_group = QGroupBox("📊 Vue d'ensemble")
        stats_layout = QVBoxLayout()

        self.stats_nb_files = QLabel("Fichiers: -")
        self.stats_nb_lines = QLabel("Lignes totales: -")
        self.stats_total_amount = QLabel("Montant total: -")
        self.stats_avg_amount = QLabel("Montant moyen: -")

        for label in [self.stats_nb_files, self.stats_nb_lines,
                      self.stats_total_amount, self.stats_avg_amount]:
            label.setStyleSheet("padding: 5px; font-size: 14px;")
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Groupe seuil minimum de commande
        threshold_group = QGroupBox("⚠️ Seuil Minimum")
        threshold_layout = QVBoxLayout()

        threshold_input_layout = QHBoxLayout()
        threshold_input_layout.addWidget(QLabel("Minimum:"))

        self.threshold_input = QLabel("0 €")
        self.threshold_input.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            padding: 5px;
            border-radius: 3px;
        """)
        threshold_input_layout.addWidget(self.threshold_input)

        threshold_layout.addLayout(threshold_input_layout)

        self.threshold_progress = QProgressBar()
        self.threshold_progress.setTextVisible(True)
        self.threshold_progress.setFormat("%v / %m €")
        threshold_layout.addWidget(self.threshold_progress)

        self.threshold_status = QLabel("Status: -")
        self.threshold_status.setStyleSheet("padding: 5px;")
        threshold_layout.addWidget(self.threshold_status)

        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)

        # Détails par fichier
        details_group = QGroupBox("📄 Détails par fichier")
        details_layout = QVBoxLayout()

        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setFrameShape(QFrame.NoFrame)

        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setSpacing(5)

        self.details_scroll.setWidget(self.details_widget)
        details_layout.addWidget(self.details_scroll)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        layout.addStretch()

        return widget

    def load_suppliers_config(self):
        """Charge la configuration des fournisseurs"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "suppliers.json"

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.suppliers_config = config.get('suppliers', [])

            # Créer les boutons fournisseurs
            self.supplier_buttons = {}

            for supplier in self.suppliers_config:
                if not supplier.get('active', True):
                    continue

                btn = QPushButton(f"  {supplier['name']}")
                btn.setCheckable(True)
                btn.setProperty('supplier_id', supplier['id'])
                btn.clicked.connect(lambda checked, s=supplier: self.filter_by_supplier(s))

                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 10px;
                        border: 2px solid #ddd;
                        border-radius: 5px;
                        background-color: white;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                    }
                    QPushButton:checked {
                        background-color: #2196F3;
                        color: white;
                        border-color: #2196F3;
                    }
                """)

                self.suppliers_layout.addWidget(btn)
                self.supplier_buttons[supplier['id']] = btn

            self.suppliers_layout.addStretch()

        except Exception as e:
            logger.error(f"Erreur chargement config fournisseurs: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur chargement config:\n{str(e)}")

    def load_today_files(self):
        """Charge les fichiers du jour depuis le serveur FTP"""
        try:
            self.files_table.setRowCount(0)
            self.files_list = []

            # Connexion SFTP
            host = os.getenv("FTP_HOST")
            port = int(os.getenv("FTP_PORT", 22))
            username = os.getenv("FTP_USERNAME")
            password = os.getenv("FTP_PASSWORD")
            ftp_path = os.getenv("FTP_PATH", "/")

            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)

            # Lister les fichiers (exclure 'old')
            files_attr = sftp.listdir_attr(ftp_path)

            today = date.today()

            for file_attr in files_attr:
                filename = file_attr.filename

                # Exclure les dossiers
                from stat import S_ISDIR
                if S_ISDIR(file_attr.st_mode):
                    continue

                # Exclure les fichiers périmés
                if filename.startswith('XX-PERIME-XX'):
                    continue

                # Extraire le fournisseur depuis le nom de fichier
                supplier_name = filename.split('-')[0] if '-' in filename else "Inconnu"

                file_date = datetime.fromtimestamp(file_attr.st_mtime).date()

                self.files_list.append({
                    'filename': filename,
                    'supplier': supplier_name,
                    'date': file_date,
                    'size': file_attr.st_size,
                    'analyzed': False
                })

            sftp.close()
            transport.close()

            # Afficher dans le tableau
            self.display_files()

            logger.info(f"{len(self.files_list)} fichier(s) chargé(s)")

        except Exception as e:
            logger.error(f"Erreur chargement fichiers: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")

    def display_files(self, filtered: Optional[List] = None):
        """Affiche les fichiers dans le tableau"""
        files_to_display = filtered if filtered is not None else self.files_list

        self.files_table.setRowCount(len(files_to_display))

        for i, file_info in enumerate(files_to_display):
            # Nom fichier
            self.files_table.setItem(i, 0, QTableWidgetItem(file_info['filename']))

            # Fournisseur
            self.files_table.setItem(i, 1, QTableWidgetItem(file_info['supplier']))

            # Date
            date_str = file_info['date'].strftime('%d/%m/%Y')
            self.files_table.setItem(i, 2, QTableWidgetItem(date_str))

            # Taille
            size_mb = file_info['size'] / (1024 * 1024)
            self.files_table.setItem(i, 3, QTableWidgetItem(f"{size_mb:.2f} MB"))

            # Analysé
            analyzed = "✓" if file_info['analyzed'] else "-"
            analyzed_item = QTableWidgetItem(analyzed)
            if file_info['analyzed']:
                analyzed_item.setForeground(QColor(76, 175, 80))
            self.files_table.setItem(i, 4, analyzed_item)

        self.files_count_label.setText(f"{len(files_to_display)} fichier(s)")

    def filter_by_supplier(self, supplier: Optional[Dict]):
        """Filtre les fichiers par fournisseur"""
        self.selected_supplier = supplier

        # Désélectionner tous les boutons
        self.all_suppliers_btn.setChecked(supplier is None)

        for btn in self.supplier_buttons.values():
            btn.setChecked(False)

        if supplier:
            # Sélectionner le bouton du fournisseur
            if supplier['id'] in self.supplier_buttons:
                self.supplier_buttons[supplier['id']].setChecked(True)

            # Filtrer les fichiers
            patterns = supplier.get('file_patterns', [])

            filtered = []
            for file_info in self.files_list:
                filename = file_info['filename']

                # Vérifier si le fichier correspond aux patterns
                import fnmatch
                for pattern in patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        filtered.append(file_info)
                        break

            self.display_files(filtered)

            # Mettre à jour les statistiques
            self.update_stats(filtered)

            # Mettre à jour le seuil si configuré
            # TODO: charger depuis config fournisseur
            self.update_threshold(supplier.get('min_order', 0))

        else:
            # Afficher tous les fichiers
            self.display_files()
            self.update_stats(self.files_list)

    def analyze_selected_files(self):
        """Analyse les fichiers affichés"""
        # Récupérer les fichiers visibles
        visible_files = []
        for i in range(self.files_table.rowCount()):
            filename = self.files_table.item(i, 0).text()
            visible_files.append(filename)

        if not visible_files:
            QMessageBox.information(self, "Info", "Aucun fichier à analyser")
            return

        # Lancer l'analyse
        ftp_path = os.getenv("FTP_PATH", "/")

        self.analyzer = FileAnalyzer(visible_files, ftp_path)
        self.analyzer.progress.connect(self.on_analysis_progress)
        self.analyzer.finished.connect(self.on_analysis_finished)
        self.analyzer.error.connect(self.on_analysis_error)
        self.analyzer.start()

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("⏳ Analyse en cours...")

    def on_analysis_progress(self, message: str):
        """Affiche la progression de l'analyse"""
        self.statusBar().showMessage(message)

    def on_analysis_finished(self, results: Dict):
        """Appelé quand l'analyse est terminée"""
        self.analysis_results = results

        # Marquer les fichiers comme analysés
        for file_info in self.files_list:
            if file_info['filename'] in results:
                file_info['analyzed'] = True

        # Rafraîchir l'affichage
        self.display_files()

        # Mettre à jour les statistiques
        visible_files = [
            f for f in self.files_list
            if any(self.files_table.item(i, 0).text() == f['filename']
                   for i in range(self.files_table.rowCount()))
        ]
        self.update_stats(visible_files)

        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🔍 Analyser les fichiers")

        QMessageBox.information(
            self,
            "Analyse terminée",
            f"{len(results)} fichier(s) analysé(s) avec succès"
        )

    def on_analysis_error(self, error: str):
        """Appelé en cas d'erreur d'analyse"""
        logger.error(f"Erreur analyse: {error}")
        self.statusBar().showMessage(f"Erreur: {error}", 5000)

    def update_stats(self, files: List[Dict]):
        """Met à jour les statistiques"""
        total_lines = 0
        total_amount = 0.0
        analyzed_count = 0

        # Effacer les détails précédents
        while self.details_layout.count():
            child = self.details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for file_info in files:
            filename = file_info['filename']

            if filename in self.analysis_results:
                result = self.analysis_results[filename]
                total_lines += result['rows']
                total_amount += result['total']
                analyzed_count += 1

                # Ajouter un widget de détail
                detail_widget = self.create_file_detail_widget(filename, result)
                self.details_layout.addWidget(detail_widget)

        # Mettre à jour les labels
        self.stats_nb_files.setText(f"Fichiers: {len(files)} ({analyzed_count} analysés)")
        self.stats_nb_lines.setText(f"Lignes totales: {total_lines:,}")
        self.stats_total_amount.setText(f"Montant total: {total_amount:,.2f} €")

        if analyzed_count > 0:
            avg = total_amount / analyzed_count
            self.stats_avg_amount.setText(f"Montant moyen: {avg:,.2f} €")
        else:
            self.stats_avg_amount.setText("Montant moyen: -")

        # Mettre à jour la barre de progression du seuil
        if self.selected_supplier:
            min_order = self.selected_supplier.get('min_order', 0)
            if min_order > 0:
                self.threshold_progress.setMaximum(int(min_order))
                self.threshold_progress.setValue(int(total_amount))

                if total_amount >= min_order:
                    self.threshold_status.setText(f"✅ Seuil atteint (+{total_amount - min_order:.2f} €)")
                    self.threshold_status.setStyleSheet("color: green; font-weight: bold; padding: 5px;")
                else:
                    remaining = min_order - total_amount
                    self.threshold_status.setText(f"❌ Manque {remaining:.2f} €")
                    self.threshold_status.setStyleSheet("color: red; font-weight: bold; padding: 5px;")

    def create_file_detail_widget(self, filename: str, result: Dict) -> QWidget:
        """Crée un widget de détail pour un fichier"""
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(3)

        # Nom fichier
        name_label = QLabel(f"📄 {filename}")
        name_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(name_label)

        # Stats
        lines_label = QLabel(f"Lignes: {result['rows']:,}")
        amount_label = QLabel(f"Montant: {result['total']:,.2f} €")

        for label in [lines_label, amount_label]:
            label.setStyleSheet("font-size: 11px; color: #555;")
            layout.addWidget(label)

        return widget

    def update_threshold(self, min_order: float):
        """Met à jour l'affichage du seuil minimum"""
        self.threshold_input.setText(f"{min_order:.0f} €")
        self.threshold_progress.setMaximum(int(min_order) if min_order > 0 else 100)
