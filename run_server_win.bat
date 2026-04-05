@echo off
setlocal
cd /d %~dp0

echo ========================================================
echo        INICIANDO SERVIDOR REMOTO DE JARVIS (V2)
echo ========================================================

:: Verificar entorno .venv
if not exist ".venv" (
    echo [ERROR] No se encontro la carpeta del entorno virtual. 
    echo Por favor, ejecuta primero run_jarvis_win.bat para instalar todo.
    pause
    exit /b 1
)

:: Activar entorno
call .venv\Scripts\activate.bat

echo [SERVIDOR]: Jarvis esta atento a la red en el puerto 8000.
echo [SERVIDOR]: Use Ctrl+C para apagarlo.
echo.

:: Correr el servidor Flask
python server_app.py

:: Pausa forzosa por si algo sale mal
echo.
echo [INFO]: El proceso ha terminado.
pause
deactivate
exit /b 0
