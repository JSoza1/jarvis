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
:: Verificamos que version de Python esta usando realmente el entorno
python --version 
:: Primero asegurar que pip, setuptools y wheel estén actualizados (soluciona muchos errores de instalación)
python -m pip install --upgrade pip setuptools wheel

:: Intentar instalar desde el archivo de requerimientos completo (SIN --quiet para ver el error)
pip install -r requirements-full.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Error durante la instalacion de dependencias.
    echo.
    echo Esto suele ocurrir porque faltan las Herramientas de Compilacion de C++.
    echo Para solucionarlo:
    echo 1. Descarga e instala "Microsoft C++ Build Tools" desde:
    echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo 2. Durante la instalacion, asegúrate de marcar la opcion:
    echo    "Desarrollo para el escritorio con C++" (Desktop development with C++)
    echo.
    echo Alternativamente, si usas Python 3.12 o superior, asegúrate de que tu version 
    echo de Python no sea una version experimental (como Python 3.13/3.14).
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
