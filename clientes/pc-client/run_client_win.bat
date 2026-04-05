@echo off
setlocal
cd /d %~dp0

echo ========================================================
echo        JARVIS PC-CLIENT
echo ========================================================

:: Verificar Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python en el PATH.
    pause
    exit /b 1
)

:: Crear Entorno .venv
if not exist ".venv" (
    echo [INFO] Creando el entorno virtual del cliente...
    python -m venv .venv
    echo [OK] Entorno virtual creado.
)

:: Activar entorno
call .venv\Scripts\activate.bat

:: Instalar dependencias necesarias para VOZ y RED
echo [INFO] Instalando librerias de comunicacion y voz masiva...
pip install speechrecognition requests python-dotenv colorama edge-tts pygame --quiet --disable-pip-version-check
pip install pyaudio --quiet --disable-pip-version-check

if errorlevel 1 (
    echo [ERROR] Fallo al instalar las nuevas librerias de voz/audio.
    pause
)

:: Crear .env inicial si no existe
if not exist ".env" (
    echo SERVER_IP=127.0.0.1 > .env
    echo SERVER_PORT=8000 >> .env
    echo [INFO] Archivo .env generado. Editalo con la IP de tu PC principal.
)

echo.
echo ========================================================
echo [OK] Cliente Multimedia listo. Conectando...
echo ========================================================
echo.

python client_main.py

pause
deactivate
exit /b 0
