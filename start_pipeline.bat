@echo off
REM Script pour lancer le pipeline avec le bon interpréteur Python
echo Lancement du pipeline BI...
"C:\Users\Aminos\AppData\Local\Programs\Python\Python313\python.exe" scripts/main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Une erreur est survenue wess.
    pause
    exit /b %ERRORLEVEL%
)
echo.
echo Pipeline termine avec succes.
pause
