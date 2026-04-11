import os
import sys
import subprocess
import time
import datetime
import requests
from ai_config import configuracion_ia
import ai_models

class CommandHandler:
    def __init__(self, tts_engine_reference):
        """
        Gestor central de inteligencia. Soporta modo servidor y local.
        """
        self.tts = tts_engine_reference
        
        print("\n--- INICIANDO CEREBROS DE IA ---")
        
        # --- MOTOR PRINCIPAL ---
        self.cliente_p, self.tipo_p = self._inicializar_motor(
            "Principal",
            configuracion_ia.api_key_principal, 
            configuracion_ia.base_url_principal
        )
        self.modelo_p = configuracion_ia.modelo_ia_principal
        self.p_agotado = False
        
        # --- MOTOR DE RESPALDO ---
        self.cliente_r, self.tipo_r = self._inicializar_motor(
            "Respaldo",
            configuracion_ia.api_key_respaldo, 
            configuracion_ia.base_url_respaldo
        )
        self.modelo_r = configuracion_ia.modelo_ia_respaldo
        self.r_agotado = False
        print("--------------------------------\n")

        # ==========================================
        # CONFIGURACIÓN DE COMANDOS LOCALES (Fácil de extender)
        # ==========================================
        # Para añadir más programas, solo copia uno de estos { diccionarios }
        # e intercambia los valores por lo que necesites abrir.
        self.comandos_locales = [

            # =========================================================================
            # PLANTILLA / EJEMPLO: CÓMO ABRIR UN SCRIPT DE PYTHON (.py)
            # (Puedes copiar este bloque exacto para crear tus propias funciones)
            # =========================================================================
            {
                # 1. NOMBRE: Etiqueta interna para saber qué hace este bloque.
                "nombre_funcionalidad": "Ejemplo Py (Scripts)",
                # 2. PALABRAS CLAVE: Si le dices "ejecuta prueba" Jarvis lo detectará.
                "palabras_clave": ["ejecuta prueba", "corre el script"],
                # 3. RESPUESTA DE JARVIS: Feedback auditivo.
                "respuesta_voz": "Ejecutando el script de prueba en segundo plano.",
                # 4. TIPO DE ACCIÓN: Siempre "abrir_programa" para ejecutar archivos externos.
                "tipo_accion": "abrir_programa",
                # 5. RUTA VARIABLE: Si guardas la ruta en el Sistema. Deja vacío "" si no usas.
                "ubicacion_env": "",
                # 6. RUTA POR DEFECTO: Dónde está guardado tu .py (solo nombre "si esta en la misma carpeta" o ruta C:\\...)
                "archivo_predeterminado": "mi_script_prueba.py",
                # 7. ¿ES UN SCRIPT .PY?: ¡Al poner 'True' se corre separado sin colgar a Jarvis!
                "es_script_python": True
            },

            {
                "nombre_funcionalidad": "Navegador",
                "palabras_clave": ["abri navegador", "abrir navegador", "abrir google", "navegador", "internet", "chrome"],
                "respuesta_voz": "Orden recibida: abriendo navegador.",
                "tipo_accion": "abrir_programa",
                # IMPORTANTE: Busca primero en tu sistema operativo esta variable. Si no existe, usa "archivo_predeterminado".
                "ubicacion_env": "JARVIS_RUTA_NAVEGADOR",
                "archivo_predeterminado": "abrir_google.bat",
                "es_script_python": False
            },

            {
                "nombre_funcionalidad": "Apagar Jarvis",
                "palabras_clave": ["chau jarvis", "detener programa", "adiós", "salir", "apágate", "apagate", "apagar programa"],
                "respuesta_voz": "Cerrando sesión por orden de voz. Hasta pronto.",
                "tipo_accion": "sistema_apagar"
            },

            {
                # 1. NOMBRE: Etiqueta interna para saber qué hace este bloque.
                "nombre_funcionalidad": "Cazador_De_Chambas",
                # 2. PALABRAS CLAVE: Si le dices "ejecuta prueba" Jarvis lo detectará.
                "palabras_clave": ["Inicia el cazador", "Prende el cazador", "enciende el cazador de chambas", "inicia el cazador de chambas", "enciende el cazador", "inicia el cazador", "enciende el cazador de chambas", "inicia el cazador de chambas", "enciende el cazador de chambas", "inicia el cazador de chambas", "abri el cazador", "abre el cazador"],
                # 3. RESPUESTA DE JARVIS: Feedback auditivo.
                "respuesta_voz": "Iniciando el cazador de chambas",
                # 4. TIPO DE ACCIÓN: Siempre "abrir_programa" para ejecutar archivos externos.
                "tipo_accion": "abrir_programa",
                # 5. RUTA VARIABLE: Si guardas la ruta en el Sistema. Deja vacío "" si no usas.
                "ubicacion_env": "CAZADOR",
                # 6. RUTA POR DEFECTO: Dónde está guardado tu .py (solo nombre "si esta en la misma carpeta" o ruta C:\\...)
                "archivo_predeterminado": "cazador_de_chambas.py",
                # 7. ¿ES UN SCRIPT .PY?: ¡Al poner 'True' se corre separado sin colgar a Jarvis!
                "es_script_python": False
            },

            {
                "nombre_funcionalidad": "Cerrar_Cazador_De_Chambas",
                "palabras_clave": ["apaga el cazador", "cierra el cazador", "detén el cazador", "deten el cazador", "apagar el cazador", "cerrar el cazador", "apaga el cazador de chambas", "cierra el cazador de chambas", "detener el cazador de chambas", "deten el cazador de chambas", "apagar el cazador de chambas", "cerrar el cazador de chambas"],
                "respuesta_voz": "Apagando el cazador de chambas.",
                "tipo_accion": "cerrar_programa",
                "archivo_predeterminado": "cazador_de_chambas"
            },

            {
                "nombre_funcionalidad": "Desactivar_Aplausos",
                "palabras_clave": ["sin aplausos", "desactivar aplausos", "para los aplausos", "no escuches aplausos"],
                "respuesta_voz": "Entendido. Ignoraré los aplausos hasta que me lo indiques.",
                "tipo_accion": "toggle_aplausos",
                "valor_toggle": False
            },

            {
                "nombre_funcionalidad": "Activar_Aplausos",
                "palabras_clave": ["activar aplausos", "escucha aplausos", "vuelve a escuchar aplausos", "activa aplausos", "activa aplauso"],
                "respuesta_voz": "Perfecto. Volveré a reaccionar ante los aplausos.",
                "tipo_accion": "toggle_aplausos",
                "valor_toggle": True
            },

            {
                "nombre_funcionalidad": "Clima_Buenos_Aires",
                "palabras_clave": ["temperatura", "clima", "tiempo", "cuanto hace", "cuánto hace", "qué temperatura", "que temperatura", "como esta el clima", "cómo está el clima"],
                "respuesta_voz": None,
                "tipo_accion": "clima"
            }
        ]

    def _inicializar_motor(self, rol, clave, url_base):
        """Inicialización dinámica según el tipo de API Key."""
        if not clave or any(x in clave for x in ["aqui", "otra_clave", "..."]):
            return None, "NINGUNO"
        
        try:
            if clave.startswith("AIzaSy"):
                print(f"[OK]: Motor {rol} CARGADO -> GOOGLE GEMINI (REST)")
                return clave, "GOOGLE"
            elif clave.startswith("gsk_"):
                print(f"[OK]: Motor {rol} CARGADO -> GROQ (REST)")
                return clave, "GROQ"
            else:
                # Caso por defecto: OpenAI o compatible
                print(f"[OK]: Motor {rol} CARGADO -> OPENAI (REST)")
                return (clave, url_base), "OPENAI"
        except Exception as e:
            print(f"[ERROR]: Fallo al cargar motor {rol}: {e}")
            return None, "NINGUNO"

    def ejecutar_rutina_aplauso(self):
        """
        Rutina de aplauso: se ejecuta al detectar dos aplausos.
        Siempre activa, incluso si Jarvis está dormido.
        Configura programas y URLs desde el .env (separados por coma).
        """
        import webbrowser
        chrome = os.getenv("JARVIS_CHROME", "").strip()

        # --- ACCIÓN 1: Abrir programas MAXIMIZADOS ---
        # JARVIS_APLAUSO_PROGRAMAS=C:\ruta\prog1.exe, C:\ruta\prog2.exe
        for ruta in os.getenv("JARVIS_APLAUSO_PROGRAMAS", "").split(","):
            ruta = ruta.strip()
            if not ruta:
                continue
            try:
                if sys.platform == "win32":
                    # SW_SHOWMAXIMIZED = 3 → la ventana arranca maximizada
                    si = subprocess.STARTUPINFO()
                    si.dwFlags = subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = 3
                    subprocess.Popen([ruta], startupinfo=si)
                else:
                    os.startfile(ruta)
            except Exception as e:
                print(f"[RUTINA APLAUSO]: No se pudo abrir '{ruta}' -> {e}")

        # --- ACCIÓN 2: Abrir URLs en una sola ventana Chrome maximizada ---
        # Todas las URLs se pasan de una sola vez → Chrome las abre como pestañas en 1 ventana
        urls = [u.strip() for u in os.getenv("JARVIS_APLAUSO_URLS", "").split(",") if u.strip()]
        if urls:
            try:
                if chrome:
                    subprocess.Popen([chrome, "--start-maximized"] + urls)
                else:
                    for url in urls:
                        webbrowser.open_new_tab(url)
            except Exception as e:
                print(f"[RUTINA APLAUSO]: No se pudo abrir URLs -> {e}")

        # --- ACCIÓN 3: Abrir YouTube en su propia ventana de Chrome ---
        yt_url = os.getenv("JARVIS_YOUTUBE_URL", "").strip()
        if yt_url and chrome:
            try:
                # PAUSA CRÍTICA: Esperamos 2 segundos para que Chrome no mezcle ventanas
                time.sleep(2) 
                subprocess.Popen([chrome, "--new-window", yt_url])
            except Exception as e:
                print(f"[RUTINA APLAUSO]: No se pudo abrir YouTube -> {e}")
        elif yt_url:
            webbrowser.open_new(yt_url)

        # --- ACCIÓN 4: Jarvis habla ---
        self.tts.speak("Hora de trabajar", mudo=False)
        self.obtener_clima(mudo=False)



    def ejecutar_comando_local(self, entrada_voz, mudo=False):
        """Procesa la entrada de voz buscando coincidencias con los comandos locales configurados en el __init__."""
        texto_limpio = entrada_voz.lower()
        
        # Iteramos sobre nuestra lista de comandos fáciles de configurar
        for comando in self.comandos_locales:
            
            # Revisar si el usuario mencionó alguna de las palabras clave de este bloque
            if any(palabra == texto_limpio or palabra in texto_limpio for palabra in comando.get("palabras_clave", [])):
                
                # Feedback auditivo de Jarvis (solo si hay una respuesta definida)
                resp = comando.get("respuesta_voz")
                if resp:
                    self.tts.speak(resp, mudo=mudo)

                tipo_accion = comando.get("tipo_accion")

                # =====================================
                # ACCIÓN: ABRIR ALGO EXTERNO A JARVIS
                # =====================================
                if tipo_accion == "abrir_programa":
                    proc = self._abrir_programa_totalmente_independiente(
                        ruta_env=comando.get("ubicacion_env"), # Variable de SO
                        ruta_defecto=comando.get("archivo_predeterminado"), # Archivo normal si no encuentra la EnvVar
                        es_python=comando.get("es_script_python", False), # Si es .py lo trata diferente
                        mudo=mudo
                    )
                    if proc and hasattr(proc, 'pid'):
                        if not hasattr(self, 'mis_hijos_pid'): self.mis_hijos_pid = []
                        self.mis_hijos_pid.append(proc.pid)
                        
                    time.sleep(1)
                    return True # El comando fue efectuado con exito

                # =====================================
                # ACCIÓN: APAGAR JARVIS
                # =====================================
                elif tipo_accion == "sistema_apagar":
                    def apagar_con_retardo():
                        time.sleep(2) # Retardo para responder a peticiones externas antes de suicidarse
                        print("\n[SISTEMA]: Apagado remoto solicitado. Cerrando servidor...")
                        os._exit(0)
                        
                    import threading
                    threading.Thread(target=apagar_con_retardo).start()
                    return True 

                # =====================================
                # ACCIÓN: CERRAR PROCESO LIMPIO
                # =====================================
                elif tipo_accion == "cerrar_programa":
                    fragmento_ruta = comando.get("archivo_predeterminado", "")
                    if fragmento_ruta:
                        try:
                            if sys.platform == "win32":
                                # --- LA BALA DE PLATA: Si Jarvis lo abrió, tiene su DNI (PID) literal ---
                                if hasattr(self, 'mis_hijos_pid'):
                                    for child_pid in self.mis_hijos_pid:
                                        print(f"[SISTEMA]: Encontrado proceso hijo de Jarvis con PID {child_pid}, liquidando su linaje...")
                                        subprocess.run(f'taskkill /PID {child_pid} /F /T', shell=True, capture_output=True)
                                    self.mis_hijos_pid.clear()
                                
                                # Tambien matamos el Chrome driver/Chrome hijo que pueda quedar colgado y huerfano en el PC
                                subprocess.run('taskkill /F /IM chromedriver.exe /T', shell=True, capture_output=True)
                            else:
                                # --- LA BALA DE PLATA adaptada para LINUX/MAC/TERMUX ---
                                if hasattr(self, 'mis_hijos_pid'):
                                    for child_pid in self.mis_hijos_pid:
                                        print(f"[SISTEMA]: Encontrado proceso hijo de Jarvis en Linux/Termux con PID {child_pid}, liquidando...")
                                        # kill -9 elimina el proceso sin preguntar
                                        subprocess.run(f'kill -9 {child_pid}', shell=True, capture_output=True)
                                    self.mis_hijos_pid.clear()
                                    
                                # Opcional de respaldo: pkill caza todos los procesos que tengan la palabra clave y los mata.
                                subprocess.run(['pkill', '-f', fragmento_ruta.replace('%', '')], capture_output=True)
                        except Exception as e:
                            print(f"[ERROR]: No se pudo localizar ni cerrar el script '{fragmento_ruta}': {e}")
                    return True
                
                # =====================================
                # ACCIÓN: TOGGLE DE APLAUSOS
                # =====================================
                elif tipo_accion == "toggle_aplausos":
                    nuevo_estado = comando.get("valor_toggle", True)
                    self.tts.aplausos_activos = nuevo_estado
                    estado_texto = "activados" if nuevo_estado else "desactivados"
                    print(f"[SISTEMA]: Aplausos {estado_texto}.")
                    return True

                # =====================================
                # ACCIÓN: CLIMA
                # =====================================
                elif tipo_accion == "clima":
                    self.obtener_clima(mudo=mudo)
                    return True


        return False # No detectó ningún comando configurado
        
    def obtener_clima(self, ciudad="Buenos Aires", mudo=False):
        """
        Consulta el clima de Buenos Aires usando wttr.in (sin API Key, sin registro).
        """
        try:
            # Pedimos el clima en español y formato de una sola línea
            url = f"https://wttr.in/{ciudad.replace(' ', '+')}?format=%t+%C&lang=es"
            resp = requests.get(url, timeout=5)
            
            # Forzamos UTF-8 para que el símbolo de grado no sea basura
            resp.encoding = 'utf-8'
            
            if resp.status_code == 200:
                texto = resp.text.strip()
                # Limpieza: "+14°C Despejado" -> "14 grados Despejado"
                texto = texto.replace("+", "").replace("°C", " grados")
                
                respuesta = f"Actualmente en {ciudad} hace {texto}."
                print(f"[CLIMA]: {respuesta}")
                self.tts.speak(respuesta, mudo=mudo)
            else:
                self.tts.speak("No pude conectar con el servicio de clima.", mudo=mudo)
        except Exception as e:
            print(f"[CLIMA ERROR]: {e}")
            self.tts.speak("Hubo un error al consultar el clima.", mudo=mudo)

    def _abrir_programa_totalmente_independiente(self, ruta_env, ruta_defecto, es_python, mudo=False):
        """
        DATO CLAVE PARA EL RENDIMIENTO: Se encarga de hacer que el nuevo programa
        corra 100% independiente. Así Jarvis no se asfixia de memoria
        ni se tilda esperando a que el otro ejecutable cierre.
        """
        # 1. Buscamos ruta según VARIABLE DE ENTORNO en la compu. 
        valor_env = os.getenv(ruta_env) if ruta_env else None
        ruta_ejecutar = valor_env
        
        # --- ALGORITMO DE BÚSQUEDA RELATIVA INTELIGENTE ---
        # Si la variable de entorno contiene el *nombre de la carpeta* (ej: "cazador_de_chambas")
        # en lugar de una ruta absoluta, buscamos esa carpeta compartiendo el directorio padre de Jarvis.
        if valor_env and not os.path.isabs(valor_env):
            # Sube un nivel desde la carpeta actual (ej: de /jarvis a nivel general)
            directorio_padre = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            carpeta_objetivo = os.path.join(directorio_padre, valor_env)
            
            # Como los proyectos de python siempre inician con main.py
            ruta_main_py = os.path.join(carpeta_objetivo, "main.py")
            if os.path.isfile(ruta_main_py):
                ruta_ejecutar = ruta_main_py
                es_python = True # Forzamos python ya que es main.py directamente
            else:
                # Si no hay main.py, buscamos el archivo predeterminado dentro de la carpeta
                ruta_ejecutar = os.path.join(carpeta_objetivo, ruta_defecto)

        # Si da vacío, usamos por ejemplo el archivo ".bat" por defecto que tengas ahí mismo
        if not ruta_ejecutar:
            print(f"[Aviso]: Usando la predeterminada. No se halló variable de entorno: '{ruta_env}'")
            ruta_ejecutar = ruta_defecto
            
        if not ruta_ejecutar: # Por si tampoco hay default configurado...
            return

        print(f"\n[SISTEMA]: Lanzando proceso independiente: {ruta_ejecutar}")

        # 2. SEPARAR EL HIJO DEL PADRE (EJECUCIÓN SEGÚN SISTEMA OPERATIVO)
        try:
            if sys.platform == "win32": # ---- WINDOWS ----
                dir_base = os.path.dirname(os.path.abspath(ruta_ejecutar))
                nombre_archivo = os.path.basename(ruta_ejecutar)
                
                if es_python:
                    # En Windows, creamos una consola explícitamente y nos desvinculamos aislando el proceso
                    proc = subprocess.Popen(['python', nombre_archivo], creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=dir_base)
                    return proc
                else:
                    # Ejecuta bats o exes de manera súper pura e independiente, aislando handles y consola
                    if ruta_ejecutar.endswith('.bat') or ruta_ejecutar.endswith('.cmd'):
                        proc = subprocess.Popen(['cmd.exe', '/c', nombre_archivo], creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=dir_base)
                        return proc
                    else:
                        os.startfile(ruta_ejecutar)
                        return None
                        
            elif "linux" in sys.platform: # ---- LINUX / TERMUX ----
                import shutil
                dir_base = os.path.dirname(os.path.abspath(ruta_ejecutar))
                nombre_archivo = os.path.basename(ruta_ejecutar)
                
                # METODO PARA ABRIR OTRA PESTAÑA / TERMINAL EN TERMUX: TMUX
                # Termux no permite "popup" de ventanas facil, TMUX es el administrador de terminales por defecto.
                if shutil.which("tmux"):
                    print(f"\n[SISTEMA TERMUX]: Abriendo OTRA TERMINAL usando TMUX.")
                    sesion = os.path.basename(dir_base).replace(" ", "_")
                    
                    # El 'read' final evita que TMUX cierre la sesión de golpe si main.py genera un error rápido o termina (ej: un simple hola mundo)
                    cmd = f"python3 {nombre_archivo}; echo '\n[Proceso terminado. Presiona Enter para salir...]'; read" if es_python else f"bash {nombre_archivo}; echo '\n[Proceso terminado. Presiona Enter para salir...]'; read"
                    
                    # El argumento -c asegura que la sesión de TMUX arranque estrictamente en la carpeta de tu bot.
                    proc = subprocess.Popen(['tmux', 'new-session', '-d', '-c', dir_base, '-s', sesion, cmd], cwd=dir_base)
                    print(f"[SISTEMA TERMUX]: Escibe 'tmux a' para ver la pantalla del programa.")
                    return proc
                else:
                    print(f"\n[SISTEMA TERMUX]: TMUX no encontrado. Intentando invocar nueva terminal de Android...")
                    # METODO NATIVO INTENT: Intenta forzar a Termux a abrir una pestaña nueva sin TMUX
                    if es_python:
                        python_path = shutil.which("python3") or shutil.which("python") or '/data/data/com.termux/files/usr/bin/python3'
                        
                        # am startservice lanza un service que le dice a Termux crear una nueva sesion interactiva
                        intent_cmd = [
                            'am', 'startservice', '--user', '0',
                            '-n', 'com.termux/com.termux.app.RunCommandService',
                            '-a', 'com.termux.RUN_COMMAND',
                            '--es', 'com.termux.RUN_COMMAND_PATH', python_path,
                            '--es', 'com.termux.RUN_COMMAND_WORKDIR', dir_base,
                            '--ez', 'com.termux.RUN_COMMAND_BACKGROUND', 'False',
                            '--es', 'com.termux.RUN_COMMAND_SESSION_ACTION', '1',
                            '--esa', 'com.termux.RUN_COMMAND_ARGUMENTS', nombre_archivo
                        ]
                        proc = subprocess.Popen(intent_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return proc
                    else:
                        proc = subprocess.Popen(['nohup', 'bash', ruta_ejecutar], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=dir_base)
                        return proc
                    
            elif sys.platform == "darwin": # ---- MAC ----
                dir_base = os.path.dirname(os.path.abspath(ruta_ejecutar))
                if es_python:
                    proc = subprocess.Popen(['python3', ruta_ejecutar], start_new_session=True, cwd=dir_base)
                    return proc
                else:
                    proc = subprocess.Popen(['open', ruta_ejecutar], start_new_session=True, cwd=dir_base)
                    return proc

        except Exception as e:
            print(f"[ERROR SISTEMA]: No se pudo abrir {ruta_ejecutar}. Razón: {e}")
            self.tts.speak("Hubo un problema. No pude encontrar la ruta del archivo que me pediste abrir.", mudo=mudo)

    def procesar_consulta_ia(self, entrada_voz, mudo=False):
        """Procesa voz localmente en el PC principal."""
        if self.cliente_p and not self.p_agotado:
            exito, resp = self._llamar_ia_core(self.cliente_p, self.tipo_p, self.modelo_p, entrada_voz)
            if exito: 
                self.tts.speak(resp, mudo=mudo)
                return True
        if self.cliente_r and not self.r_agotado:
            print(f"\n[SISTEMA]: Saltando a motor de respaldo ({self.tipo_r})...")
            exito_r, resp_r = self._llamar_ia_core(self.cliente_r, self.tipo_r, self.modelo_r, entrada_voz)
            if exito_r: 
                self.tts.speak(resp_r, mudo=mudo)
                return True
        return False

    def procesar_consulta_ia_remota(self, entrada):
        """Retorna texto puro para las peticiones de red (Servidor)."""
        if self.cliente_p and not self.p_agotado:
            exito, texto = self._llamar_ia_core(self.cliente_p, self.tipo_p, self.modelo_p, entrada)
            if exito: return texto
        if self.cliente_r and not self.r_agotado:
            exito_r, texto_r = self._llamar_ia_core(self.cliente_r, self.tipo_r, self.modelo_r, entrada)
            if exito_r: return texto_r
        return "Servidor Jarvis fuera de línea o cuota agotada."

    def _llamar_ia_core(self, cliente, tipo, modelo, entrada_voz):
        """Núcleo unificado de llamadas inteligentes usando el módulo ai_models."""
        if not cliente: return False, ""
        
        try:
            print(f"\n[SISTEMA]: Consultando a {tipo} [Modelo: {modelo}]...")
            respuesta_texto = ""
            personalidad_base = configuracion_ia.prompt_personalidad
            
            # --- INYECCIÓN DE CONTEXTO TEMPORAL ---
            # Agregamos la fecha y hora actual para que Jarvis sepa en que momento vive.
            ahora = datetime.datetime.now()
            fecha_hora_contexto = f"\n\n[CONTEXTO TEMPORAL]: Fecha: {ahora.strftime('%d/%m/%Y')}, Hora: {ahora.strftime('%H:%M:%S')}"
            personalidad = personalidad_base + fecha_hora_contexto
            
            if tipo == "GOOGLE":
                respuesta_texto = ai_models.consultar_gemini(cliente, modelo, personalidad, entrada_voz)
            
            elif tipo == "GROQ":
                respuesta_texto = ai_models.consultar_groq(cliente, modelo, personalidad, entrada_voz)
            
            elif tipo == "OPENAI":
                clave_oa, url_base_oa = cliente # cliente es una tupla (clave, url_base)
                respuesta_texto = ai_models.consultar_openai(clave_oa, url_base_oa, modelo, personalidad, entrada_voz)
            
            if respuesta_texto:
                return True, respuesta_texto
                
        except Exception as e:
            error_str = str(e).lower()
            print(f"\n[AVISO]: El motor {tipo} ha fallado -> {e}\n")
            if "429" in error_str or "limit" in error_str or "quota" in error_str:
                if tipo == self.tipo_p: self.p_agotado = True
                else: self.r_agotado = True
            return False, ""
            
        return False, ""
