@echo off
setlocal
cd /d %~dp0

echo ========================================================
echo        Iniciando JARVIS
echo ========================================================

:: Verificar si Python está instalado
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se encontro Python en tu sistema.
    echo Por favor, instala Python y asegúrate de marcar "Add to PATH".
    pause
    exit /b 1
)

:: Validar si existe el entorno virtual
if not exist ".venv" (
    echo [INFO] Creando el entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado.
)

:: Activar el entorno virtual
echo [INFO] Activando el entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Instalar dependencias si no están instaladas
echo [INFO] Verificando dependencias necesarias...
pip install speechrecognition edge-tts pygame python-dotenv requests colorama flask --quiet --disable-pip-version-check
pip install pyaudio --quiet --disable-pip-version-check

if errorlevel 1 (
    echo [ERROR] Error durante la instalacion de dependencias.
    echo Probablemente falte PyAudio. Intenta correr:
    echo pip install pipwin
    echo pipwin install pyaudio
    echo O descarga el wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    pause
    exit /b 1
)

echo.
echo ========================================================
echo [OK] Todo listo. Iniciando script de voz...
echo Comandos: "abri navegador" / "detener programa"
echo.

python main.py

if errorlevel 1 (
    echo [ERROR] El programa de Python se cerro con errores.
)

echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause
deactivate
exit /b 0
