@echo off
REM Script de lancement rapide de l'application
REM Double-cliquez sur ce fichier pour lancer l'application

echo ====================================
echo Gestionnaire Commandes Fournisseurs
echo ====================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Vérifier que l'activation a fonctionné
if errorlevel 1 (
    echo ERREUR: Impossible d'activer l'environnement virtuel.
    echo Assurez-vous que Python est installé et que vous avez exécuté:
    echo    python -m venv venv
    pause
    exit /b 1
)

echo Lancement de l'application...
echo.

REM Lancer l'application
python app\main.py

REM Si l'application se ferme avec une erreur
if errorlevel 1 (
    echo.
    echo L'application s'est terminée avec une erreur.
    echo Consultez les logs dans le dossier logs/
    pause
)
