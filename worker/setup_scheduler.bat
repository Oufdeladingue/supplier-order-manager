@echo off
REM Script pour configurer la tâche planifiée Windows
REM À exécuter en tant qu'administrateur

echo Configuration de la tâche planifiée pour la collecte des fichiers...

REM Variables à personnaliser
set TASK_NAME=CollecteCommandesFournisseurs
set PYTHON_PATH=C:\Python311\python.exe
set SCRIPT_PATH=%~dp0collector.py
set RUN_TIME=10:00

REM Créer la tâche planifiée
schtasks /Create /TN "%TASK_NAME%" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /SC DAILY /ST %RUN_TIME% /F

if %ERRORLEVEL% EQU 0 (
    echo Tâche planifiée créée avec succès!
    echo Nom: %TASK_NAME%
    echo Heure d'exécution: %RUN_TIME% tous les jours
    echo.
    echo Pour vérifier: schtasks /Query /TN "%TASK_NAME%"
    echo Pour supprimer: schtasks /Delete /TN "%TASK_NAME%" /F
) else (
    echo Erreur lors de la création de la tâche planifiée.
    echo Assurez-vous d'exécuter ce script en tant qu'administrateur.
)

pause
