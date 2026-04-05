import os

# SILENCIO DE PYGAME
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import sys
import time
import re
import requests
import asyncio
import pygame
import edge_tts
import speech_recognition as sr
from dotenv import load_dotenv
from colorama import init, Fore, Style

# INICIALIZACIÓN
init(autoreset=True)
load_dotenv()
pygame.mixer.init()

# CONFIGURACIÓN DE RED
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}/consultar"

class JarvisRemoteClient:
    def __init__(self):
        """Inicializamos oído, voz y estado de alerta de Jarvis."""
        self.reconocedor = sr.Recognizer()
        self.reconocedor.pause_threshold = 1.5
        self.voz_seleccionada = 'es-MX-JorgeNeural'
        self.archivo_voz = "remote_resp.mp3"
        
        # --- Lógica de Estado ---
        self.esta_dormido = True
        self.interrumpido = False # Bandera para detener el habla
        self.palabras_activacion = [
            "jarvis", "café", "cafe", "despierta", "activar", "iarvis"
        ]
        self.palabras_desactivacion = [
            "listo", "descansa", "silencio", "ya está", "espera", "callate", "cállate", "para", "cayate"
        ]
        self.palabras_salir = [
            "chau jarvis", "detener programa", "adiós", "salir", "apágate", "apagate", "apagar programa"
        ]

    async def _generar_audio_asincrono(self, texto):
        """Genera audio para la respuesta neuronal."""
        limpio = re.sub(r'[\*\_\#]', '', texto)
        comunicar = edge_tts.Communicate(limpio, self.voz_seleccionada)
        await comunicar.save(self.archivo_voz)

    def responder(self, texto, con_voz=True):
        """Muestra texto y reproduce audio con soporte de interrupción."""
        print(f"\n{Fore.GREEN}[Jarvis]: {texto}")
        if not con_voz: return
        
        try:
            # 1. Generar el audio
            asyncio.run(self._generar_audio_asincrono(texto))
            self.interrumpido = False
            
            # 2. SISTEMA DE INTERRUPCIÓN: Escucha reactiva mientras habla
            def _callback_interrupcion(recognizer, audio):
                try:
                    frase = recognizer.recognize_google(audio, language="es-ES").lower()
                    if any(p in frase for p in self.palabras_desactivacion):
                        print(f"\n{Fore.YELLOW}[SISTEMA]: Interrupción detectada. Jarvis se calla.")
                        self.interrumpido = True
                        pygame.mixer.music.stop() # Mata el audio
                except: pass

            # Iniciamos escucha rápida (2 seg) en fondo solo para cortes
            parar_interrupcion = self.reconocedor.listen_in_background(sr.Microphone(), _callback_interrupcion, phrase_time_limit=2)
            
            # 3. REPRODUCCIÓN
            pygame.mixer.music.load(self.archivo_voz)
            pygame.mixer.music.play()
            
            # Esperar a que termine o sea interrumpido
            while pygame.mixer.music.get_busy() and not self.interrumpido:
                time.sleep(0.1)
            
            # Limpieza post-habla
            parar_interrupcion(wait_for_stop=False)
            pygame.mixer.music.unload()
            if os.path.exists(self.archivo_voz):
                os.remove(self.archivo_voz)
                
        except Exception as e:
            print(f"{Fore.RED}[FALLO DE VOZ]: {e}")

    def procesar_logica_entrada(self, texto, es_voz=True):
        """Gestión de estados y envío a red."""
        texto_limpio = texto.strip().lower()
        if not texto_limpio: return

        # Si Jarvis está dormido, solo se despierta si se dice una palabra de activación    
        if self.esta_dormido:
            if any(palabra in texto_limpio for palabra in self.palabras_activacion):
                self.esta_dormido = False
                self.responder("Sistemas remotos activos.", con_voz=es_voz)
            return

        if any(palabra in texto_limpio for palabra in self.palabras_desactivacion):
            self.esta_dormido = True
            self.responder("Modo de espera activado.", con_voz=es_voz)
            return

        # Eliminamos la salida local para que la orden SIEMPRE llegue al servidor
        
        tipo = "[VOZ]" if es_voz else "[TEXTO]"
        print(f"\n{Fore.CYAN}{tipo}: '{texto_limpio}'")
        
        try:
            res = requests.post(SERVER_URL, json={"mensaje": texto_limpio}, timeout=15)
            if res.status_code == 200:
                respuesta = res.json()['respuesta']
                self.responder(respuesta, con_voz=es_voz)
                
                # Si Jarvis confirmó el apagado, cerramos el cliente también
                if any(p in texto_limpio for p in self.palabras_salir):
                    print(f"{Fore.YELLOW}[LOG]: El servidor aceptó la orden de apagado. Cerrando cliente en 2 seg.")
                    time.sleep(2)
                    sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}[CONEXIÓN]: Error con el servidor. {e}")

    def loop_hibrido(self, mic):
        """Gestión dual de entrada."""
        print(f"\n{Fore.WHITE}==========================================")
        print(f"      CLIENTE JARVIS PC-CLIENT ACTIVO")
        print(f"==========================================\n")
        
        def _callback(reconocedor, audio):
            try:
                # Solo procesamos voz si NO estamos interrumpiendo un discurso previo
                frase = reconocedor.recognize_google(audio, language="es-ES").lower()
                self.procesar_logica_entrada(frase, es_voz=True)
            except: pass

        # Inicia el hilo de escucha en segundo plano
        self.reconocedor.listen_in_background(mic, _callback, phrase_time_limit=12)

        # Bucle principal de entrada de texto   
        while True:
            try:
                label = "[DORMIDO]" if self.esta_dormido else "[ACTIVO]"
                entrada = input(f"\n{Fore.MAGENTA}{label} >>> ")
                if entrada.strip():
                    self.procesar_logica_entrada(entrada, es_voz=False)
            except (KeyboardInterrupt, EOFError):
                break

# Punto de entrada
if __name__ == "__main__":
    cliente = JarvisRemoteClient()
    try:
        micro = sr.Microphone()
        with micro as source:
            cliente.reconocedor.adjust_for_ambient_noise(source, duration=1)
        cliente.loop_hibrido(micro)
    except Exception as e:
        print(f"{Fore.RED}[ERROR]: {e}")
        while True:
            t = input("\n[TECLADO] >>> ")
            cliente.procesar_logica_entrada(t, es_voz=False)
