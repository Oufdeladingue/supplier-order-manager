"""
Script de compilation de l'application en exécutable avec PyInstaller
"""

import PyInstaller.__main__
import shutil
import sys
from pathlib import Path

# Forcer l'encodage UTF-8 pour la console Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Chemin du projet
project_dir = Path(__file__).parent
app_dir = project_dir / 'app'
assets_dir = project_dir / 'assets'
main_file = app_dir / 'main.py'
icon_file = assets_dir / 'logo' / 'logo.ico'

# Nettoyer les anciens builds
build_dir = project_dir / 'build'
dist_dir = project_dir / 'dist'

if build_dir.exists():
    shutil.rmtree(build_dir)
if dist_dir.exists():
    shutil.rmtree(dist_dir)

print("Compilation de l'application...")
print(f"Dossier du projet: {project_dir}")
print(f"Fichier principal: {main_file}")

# Arguments PyInstaller
args = [
    str(main_file),
    '--name=SupplierOrderManager',
    '--onefile',  # Un seul fichier exécutable
    '--windowed',  # Pas de console (interface graphique uniquement)

    # Inclure tous les modules nécessaires
    '--hidden-import=PySide6',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
    '--hidden-import=supabase',
    '--hidden-import=loguru',
    '--hidden-import=selenium',
    '--hidden-import=webdriver_manager',

    # Dossiers à inclure
    f'--add-data={app_dir / "ui"};app/ui',
    f'--add-data={app_dir / "services"};app/services',
    f'--add-data={app_dir / "models"};app/models',
    f'--add-data={app_dir / "utils"};app/utils',
    f'--add-data={assets_dir};assets',  # Inclure les assets (icônes, logos)

    # Options de build
    '--clean',
    '--noconfirm',

    # Optimisations
    '--optimize=2',
]

# Ajouter l'icône si elle existe
if icon_file.exists():
    args.insert(4, f'--icon={icon_file}')
    print(f"Icone de l'application: {icon_file}")
else:
    print("Attention: Icone introuvable, l'executable utilisera l'icone par defaut")

PyInstaller.__main__.run(args)

print("\nCompilation terminee!")
print(f"Executable disponible dans: {dist_dir / 'SupplierOrderManager.exe'}")
print("\nProchaines etapes:")
print("1. Tester l'executable dans dist/SupplierOrderManager.exe")
print("2. Creer un depot GitHub")
print("3. Creer une release v1.0.0 avec cet executable")
