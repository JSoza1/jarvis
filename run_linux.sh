#!/bin/bash

# ========================================================
#       JARVIS SERVER - Lanzador Linux / Termux
# ========================================================

# Aseguramos que estamos en la carpeta del proyecto
cd "$(dirname "$0")"

echo "--------------------------------------------------------"
echo "        INICIANDO JARVIS SERVER (LINUX / TERMUX)"
echo "--------------------------------------------------------"

# 1. ¿Está Python3 instalado?
if ! command -v python3 &> /dev/null
then
    echo "[ERROR]: Python3 no detectado. Instálalo con: pkg install python"
    exit 1
fi

# 2. Gestionar el Entorno Virtual (.venv_linux)
if [ ! -d ".venv_linux" ]; then
    echo "[INFO]: Creando entorno virtual nuevo (.venv_linux)..."
    python3 -m venv .venv_linux
fi

# 3. Activar el entorno
source .venv_linux/bin/activate

# 4. Instalación de dependencias optimizadas (REST Only)
echo "[INFO]: Verificando y descargando dependencias Lite..."
pip install --upgrade pip --quiet

# Verificamos si existe el archivo de requisitos
if [ -f "requirements.txt" ]; then
    echo "[INFO]: Instalando desde requirements.txt..."
    pip install -r requirements.txt
else
    echo "[AVISO]: No se encontro requirements.txt. Instalando manualmente..."
    pip install flask requests python-dotenv colorama
fi

# 5. Verificación final de librerías críticas (Flask es el corazón del server)
if ! python3 -c "import flask" &> /dev/null; then
    echo ""
    echo "--------------------------------------------------------"
    echo "[FALLO CRÍTICO]: No se pudieron instalar las librerías."
    echo "--------------------------------------------------------"
    echo "Si ves errores de librerías, ejecuta esto en Termux:"
    echo "pkg install -y openssl libffi rust python binutils make clang"
    echo "--------------------------------------------------------"
    deactivate
    exit 1
fi

# 6. Arranque del Servidor
echo "--------------------------------------------------------"
echo "[OK]: Cerebro de Jarvis (REST) activo en puerto 8000."
echo "[OK]: Listo para recibir órdenes desde tus clientes."
echo "--------------------------------------------------------"

python3 server_app.py

# Si el servidor se apaga por error
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR]: El servidor ha fallado. Revisa los logs arriba."
fi

deactivate
