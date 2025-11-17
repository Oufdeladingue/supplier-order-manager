"""
Service de traitement et transformation des fichiers fournisseurs
"""

import os
import pandas as pd
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from loguru import logger

from app.models.file_record import FileType


class FileProcessor:
    """Classe pour traiter et transformer les fichiers fournisseurs"""

    def __init__(self, temp_folder: str = "./temp"):
        self.temp_folder = Path(temp_folder)
        self.temp_folder.mkdir(parents=True, exist_ok=True)

    def read_file(self, file_path: str, file_type: FileType) -> Optional[pd.DataFrame]:
        """Lit un fichier et retourne un DataFrame pandas"""
        try:
            if file_type == FileType.CSV:
                # Essayer différents encodages
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"Fichier CSV lu avec encoding {encoding}: {file_path}")
                        return df
                    except UnicodeDecodeError:
                        continue
                logger.error(f"Impossible de lire le fichier CSV avec les encodages testés: {file_path}")
                return None

            elif file_type in [FileType.XLSX, FileType.XLS]:
                df = pd.read_excel(file_path)
                logger.info(f"Fichier Excel lu: {file_path}")
                return df

            else:
                logger.error(f"Type de fichier non supporté: {file_type}")
                return None

        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            return None

    def apply_transformation(self, df: pd.DataFrame, rules: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Applique les règles de transformation à un DataFrame

        Règles supportées:
        - column_mapping: renommage de colonnes
        - columns_to_add: ajout de colonnes avec valeurs par défaut
        - columns_to_remove: suppression de colonnes
        - format_rules: formatage des valeurs
        """
        try:
            result_df = df.copy()

            # 1. Renommage des colonnes
            if 'column_mapping' in rules and rules['column_mapping']:
                result_df = result_df.rename(columns=rules['column_mapping'])
                logger.debug(f"Colonnes renommées: {rules['column_mapping']}")

            # 2. Ajout de colonnes
            if 'columns_to_add' in rules and rules['columns_to_add']:
                for col_name, col_value in rules['columns_to_add'].items():
                    if col_value == 'today':
                        result_df[col_name] = datetime.now().date()
                    elif col_value == 'now':
                        result_df[col_name] = datetime.now()
                    else:
                        result_df[col_name] = col_value
                logger.debug(f"Colonnes ajoutées: {list(rules['columns_to_add'].keys())}")

            # 3. Suppression de colonnes
            if 'columns_to_remove' in rules and rules['columns_to_remove']:
                result_df = result_df.drop(columns=rules['columns_to_remove'], errors='ignore')
                logger.debug(f"Colonnes supprimées: {rules['columns_to_remove']}")

            # 4. Règles de formatage
            if 'format_rules' in rules and rules['format_rules']:
                for col_name, format_type in rules['format_rules'].items():
                    if col_name not in result_df.columns:
                        continue

                    if format_type == 'uppercase':
                        result_df[col_name] = result_df[col_name].astype(str).str.upper()
                    elif format_type == 'lowercase':
                        result_df[col_name] = result_df[col_name].astype(str).str.lower()
                    elif format_type == 'integer':
                        result_df[col_name] = pd.to_numeric(result_df[col_name], errors='coerce').fillna(0).astype(int)
                    elif format_type == 'float':
                        result_df[col_name] = pd.to_numeric(result_df[col_name], errors='coerce')
                    elif format_type == 'date':
                        result_df[col_name] = pd.to_datetime(result_df[col_name], errors='coerce')
                    elif format_type == 'trim':
                        result_df[col_name] = result_df[col_name].astype(str).str.strip()

                logger.debug(f"Formatage appliqué sur: {list(rules['format_rules'].keys())}")

            logger.info(f"Transformation appliquée avec succès. Lignes: {len(result_df)}, Colonnes: {len(result_df.columns)}")
            return result_df

        except Exception as e:
            logger.error(f"Erreur lors de la transformation: {e}")
            return None

    def save_dataframe(self, df: pd.DataFrame, output_path: str, file_type: FileType) -> bool:
        """Sauvegarde un DataFrame dans un fichier"""
        try:
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)

            if file_type == FileType.CSV:
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif file_type in [FileType.XLSX, FileType.XLS]:
                df.to_excel(output_path, index=False, engine='openpyxl')
            else:
                logger.error(f"Type de fichier non supporté pour la sauvegarde: {file_type}")
                return False

            logger.info(f"DataFrame sauvegardé: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier: {e}")
            return False

    def merge_files(self, file_paths: List[str], output_path: str,
                    file_type: FileType, supplier_code: str) -> Optional[pd.DataFrame]:
        """
        Regroupe plusieurs fichiers d'un même fournisseur en un seul
        """
        try:
            dfs = []
            for file_path in file_paths:
                df = self.read_file(file_path, file_type)
                if df is not None:
                    # Ajouter une colonne pour tracer l'origine
                    df['_source_file'] = Path(file_path).name
                    dfs.append(df)

            if not dfs:
                logger.error("Aucun fichier valide à regrouper")
                return None

            # Concaténer tous les DataFrames
            merged_df = pd.concat(dfs, ignore_index=True)

            # Sauvegarder le fichier regroupé
            if self.save_dataframe(merged_df, output_path, file_type):
                logger.info(f"Fichiers regroupés avec succès: {len(dfs)} fichiers, {len(merged_df)} lignes au total")
                return merged_df
            else:
                return None

        except Exception as e:
            logger.error(f"Erreur lors du regroupement des fichiers: {e}")
            return None

    def validate_file(self, df: pd.DataFrame, required_columns: List[str]) -> Dict[str, Any]:
        """
        Valide qu'un fichier contient les colonnes requises

        Returns:
            Dict avec 'valid' (bool) et 'missing_columns' (list)
        """
        missing_columns = [col for col in required_columns if col not in df.columns]

        return {
            'valid': len(missing_columns) == 0,
            'missing_columns': missing_columns,
            'found_columns': list(df.columns),
            'row_count': len(df)
        }

    def get_file_info(self, file_path: str, file_type: FileType) -> Optional[Dict[str, Any]]:
        """Récupère des informations sur un fichier"""
        try:
            df = self.read_file(file_path, file_type)
            if df is None:
                return None

            file_size = Path(file_path).stat().st_size

            return {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos du fichier: {e}")
            return None
