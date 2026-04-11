# 🤖 JARVIS - Asistente con IA integrada

**Jarvis** es un asistente de voz inteligente y sofisticado diseñado para Windows y Linux/Termux. Utiliza tecnología de **Voz Neuronal (Edge-TTS)** para ofrecer una experiencia auditiva humana y fluida. 

Introduce una arquitectura de **"Doble Cerebro"** con sistema de auto switch entre modelos de IA y **conexión REST**, optimizada para máxima compatibilidad.

---

## 🚀 Características Principales

-   **🔊 Voz Neuronal Humana**: Generación de audio de alta fidelidad con Microsoft Edge-TTS.
-   **🎙️ Automatización por Aplausos**: Trigger de múltiples acciones (Programas y URLs) mediante detección de doble aplauso, con gestión independiente de procesos.
-   **🌤️ Reporte de Clima**: Consulta meteorológica en tiempo real (temperatura y estado del cielo) para Buenos Aires utilizando integración nativa con wttr.in (sin necesidad de API Keys externas).
-   **🧠 Doble Cerebro (Fallback)**: Conexión nativa con 2 modelos de IA. Jarvis se cambia automáticamente al motor de respaldo si el principal falla.
-   **🎭 Personalidad Configurable**: Define cómo debe hablar y actuar Jarvis mediante una simple variable en tu `.env`.
-   **🌈 Consola con Colores**: Distinción visual por colores (Verde para Jarvis, Celeste para el Usuario) y limpieza de Markdown para una lectura de voz fluida.
-   **💤 Modo Sueño (Wake Word)**: Se activa con palabras clave como `"Jarvis"`, `"Café"` o la que se defina en el archivo command_handler.py.
-   **🔌 Zero-SDK (REST)**: Conexión ligera con Gemini, Groq y OpenAI mediante Requests, eliminando errores de librerías.
-   **🛑 Apagado en Cascada**: Apaga el cliente y el servidor de forma sincronizada con una sola orden.
-   **🛠️ Instalador Modular**: El archivo `.bat` o `.sh` gestiona automáticamente el entorno virtual (`.venv`) y las dependencias.

---

## 📂 Estructura del Proyecto

```text
jarvis/
├── .env                # Configuración real (API Keys, Modelos y Personalidad)
├── .env.example        # Plantilla con ejemplos para configurar Gemini y Groq
├── main.py             # Motor principal (Oído, Sistema de Voz y Lógica de Colores)
├── command_handler.py  # Cerebro modular con lógica de conmutación inteligente
├── ai_models.py        # Central de conexiones REST (Google, Groq, OpenAI)
├── ai_config.py        # Gestor de configuración y validación de variables de entorno
├── run_jarvis_win.bat  # Lanzador de Windows (Instalador + Ejecutor automático)
├── run_server_win.bat  # Lanzador de servidor para Windows
├── run_linux.sh        # Lanzador optimizado para Termux / Linux
├── abrir_google.bat    # Comando local de ejemplo para abrir el navegador
└── .venv/              # Entorno virtual privado (creado automáticamente)
```

---

## 🛠️ Tecnologías y Dependencias

El sistema gestiona de forma aislada las siguientes librerías:
-   **`flask`**: Servidor web ligero.
-   **`requests`**: Comunicación directa con las APIs REST de Google Gemini, Groq y OpenAI.
-   **`colorama`**: Gestión nativa de colores en la consola.
-   **`speechrecognition`**: Transcripción de voz a texto.
-   **`pygame`**: Manejo de audio e interrupciones.

---

## ⚙️ Guía de Configuración

### 1. Claves de API
Edita tu archivo `.env` configurando los dos proveedores:

```env
# Proveedor Principal (Google Gemini - Ahora via REST para mayor compatibilidad)
API_KEY_IA_1=tu_clave_gemini
BASE_URL_IA_1=https://generativelanguage.googleapis.com/v1beta/ # (Opcional, se usa la URL de Google por defecto)
MODEL_IA_1=gemini-1.5-flash

# Proveedor de Respaldo (Ejemplo: Groq)
API_KEY_IA_2=tu_clave_groq
BASE_URL_IA_2=https://api.groq.com/openai/v1
MODEL_IA_2=llama-3.3-70b-versatile

# Tu toque personal
PROMPT_PERSONALIDAD="Eres Jarvis, un asistente sofisticado y con humor argentino..."

# Automatización por Aplausos (Rutas a ejecutables y URLs separadas por coma)
JARVIS_CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
JARVIS_APLAUSO_PROGRAMAS="C:\Ruta\Al\Programa.exe"
JARVIS_APLAUSO_URLS="https://google.com,https://github.com"
JARVIS_YOUTUBE_URL="https://youtube.com/watch?v=tu_video&autoplay=1"
```

### 2. Ejecución
En windows: Simplemente haz doble clic en **`run_jarvis_win.bat`**. 
El script preparará el entorno, instalará lo que falte e iniciará a Jarvis automáticamente.

---

## 🗣️ Control de Voz y Consola

-   **Palabras de Activación**: `"Jarvis"`, `"Café"`, `"Despierta"`, `"Activar"`.
-   **Palabras de Pausa**: `"Listo"`, `"Descansa"`, `"Silencio"`, `"Espera"`.
-   **Palabras de Salida (Apagado en Cascada)**: `"Detener programa"`, `"Salir"`, `"Apágate"`. (Apaga cliente y servidor sincronizadamente).
-   **Comandos de Clima**: `"¿Qué temperatura hace?"`, `"¿Cómo está el clima?"`, `"Decime el tiempo"`.
-   **Automatización**: Activación de flujo de trabajo mediante un aplauso doble (Configurable en `.env`).
-   **Colores de Consola**: 
    -   🟢 **Verde**: Respuestas de Jarvis.
    -   🔵 **Celeste**: Lo que Jarvis escuchó o lo que tú escribiste.
    -   ⚪ **Blanco**: Mensajes del sistema y diagnósticos.

---

## 🎙️ Personalización de la Voz

Puedes cambiar la voz en la clase `JarvisEngine` dentro de `main.py`:
-   `es-MX-JorgeNeural` (Hombre - Predeterminado)
-   `es-MX-DaliaNeural` (Mujer)
-   `es-AR-TomasNeural` (Hombre - Argentina)
-   `es-ES-AlvaroNeural` (Hombre - España)

---

## 🌐 MODO RED DISTRIBUIDA

Esta versión permite separar el "Cerebro" de Jarvis de sus "Oídos". Puedes tener a Jarvis corriendo en un servidor central y controlarlo desde cualquier otra PC o dispositivo.

### 1. El Servidor (Cerebro Central)
Puedes ejecutar el servidor en Windows o en un celular con **Termux (Android)**.
-   **Windows**: Ejecuta `run_server_win.bat`.
-   **Linux / Termux**: Dale permisos y ejecuta `./run_linux.sh`.
-   **Puerto**: Escucha por defecto en el puerto **8000**.

### 2. El Cliente Remoto (Oído y Voz)
Se encuentra en la carpeta `/clientes/pc-client`. Copia esa carpeta a cualquier otra PC de tu red.
-   **Configuración**: Edita el archivo `.env` dentro de la carpeta del cliente y pon la IP de tu servidor:
    ```env
    SERVER_IP=192.168.1.XX
    SERVER_PORT=8000
    ```
-   **Arranque**: Ejecuta `run_client_win.bat`. Jarvis te escuchará y te hablará desde esa computadora remota.

---

## 🖥️ Automatización y Ventanas

Jarvis utiliza un sistema de gestión de ventanas optimizado para flujos de trabajo:
- **Maximización**: Los programas externos se abren utilizando `SW_SHOWMAXIMIZED`.
- **Navegador**: Las URLs de trabajo se agrupan en una única ventana de Chrome maximizada.
- **YouTube Focus**: YouTube se lanza en una ventana independiente (`--new-window`) con un retraso de seguridad de 2 segundos para garantizar que mantenga el foco y el `autoplay` funcione correctamente sin interferir con otras aplicaciones.

---

Desarrollado por Jsoza1