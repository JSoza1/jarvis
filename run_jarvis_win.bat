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
:: Volvemos al modo silencioso pero asegurando que use requirements-full.txt
python -m pip install --upgrade pip setuptools wheel --quiet
pip install -r requirements-full.txt --quiet

echo.
echo ========================================================
echo [OK] Todo listo. Iniciando JARVIS...
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
