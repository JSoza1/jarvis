import os
import sys
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

        # Comandos locales configurados
        self.cmd_navegador = ["abri navegador", "abrir navegador", "abrir google", "navegador", "internet", "chrome"]
        self.cmd_salir = ["chau jarvis", "detener programa", "adiós", "salir", "apágate", "apagate", "apagar programa"]

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
        """Ejecuta comandos físicos SÓLO si el sistema operativo es Windows."""
        texto_limpio = entrada_voz.lower()
        
        # Abrir Navegador (PROTECCIÓN GLOBAL para Linux/Android)
        if any(palabra in texto_limpio for palabra in self.cmd_navegador):
            if sys.platform == "win32":
                self.tts.speak("Orden recibida: abriendo navegador.", mudo=mudo)
                os.system("start abrir_google.bat")
                time.sleep(1)
                return True
            else:
                print(f"\n[SISTEMA]: Se intento abrir el navegador pero el sistema actual es {sys.platform}. Comando ignorado.")
                return False
            
        # Cerrar Jarvis
        if any(palabra == texto_limpio or palabra in texto_limpio for palabra in self.cmd_salir):
            self.tts.speak("Cerrando sesión remota por orden de voz. Hasta pronto.", mudo=mudo)
            
            # Función interna para apagar con retardo (permite enviar la respuesta HTTP antes)
            def apagar_con_retardo():
                import os
                time.sleep(2) # Damos margen para que el cliente reciba la confirmación
                print("\n[SISTEMA]: Apagado remoto solicitado. Cerrando servidor...")
                os._exit(0) # Mata el proceso hijo y el servidor Flask
                
            import threading
            threading.Thread(target=apagar_con_retardo).start()
            return True
            
        return False

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
