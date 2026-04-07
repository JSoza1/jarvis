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

    def ejecutar_comando_local(self, entrada_voz, mudo=False):
        """Procesa la entrada de voz buscando coincidencias con los comandos locales configurados en el __init__."""
        texto_limpio = entrada_voz.lower()
        
        # Iteramos sobre nuestra lista de comandos fáciles de configurar
        for comando in self.comandos_locales:
            
            # Revisar si el usuario mencionó alguna de las palabras clave de este bloque
            if any(palabra == texto_limpio or palabra in texto_limpio for palabra in comando.get("palabras_clave", [])):
                
                # Feedback auditivo de Jarvis
                if "respuesta_voz" in comando:
                    self.tts.speak(comando["respuesta_voz"], mudo=mudo)

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
                
        return False # No detectó ningún comando configurado
        
    def _abrir_programa_totalmente_independiente(self, ruta_env, ruta_defecto, es_python, mudo=False):
        """
        DATO CLAVE PARA EL RENDIMIENTO: Se encarga de hacer que el nuevo programa
        corra 100% independiente. Así Jarvis no se asfixia de memoria
        ni se tilda esperando a que el otro ejecutable cierre.
        """
        # 1. Buscamos ruta según VARIABLE DE ENTORNO en la compu. 
        ruta_ejecutar = os.getenv(ruta_env) if ruta_env else None
        
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
                        
            elif "linux" in sys.platform: # ---- LINUX ----
                if es_python:
                    dir_base = os.path.dirname(os.path.abspath(ruta_ejecutar))
                    # nohup y start_new_session evitan que matar a Jarvis cierre este proceso
                    subprocess.Popen(['nohup', 'python3', ruta_ejecutar], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=dir_base)
                else:
                    subprocess.Popen(['nohup', 'xdg-open', ruta_ejecutar], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
            elif sys.platform == "darwin": # ---- MAC ----
                if es_python:
                    dir_base = os.path.dirname(os.path.abspath(ruta_ejecutar))
                    subprocess.Popen(['python3', ruta_ejecutar], start_new_session=True, cwd=dir_base)
                else:
                    subprocess.Popen(['open', ruta_ejecutar], start_new_session=True)

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
