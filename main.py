import os
# Silenciamos el mensaje de bienvenida de pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import sys
import time
import re
import struct
import threading
from colorama import init, Fore, Style

# Inicializamos colorama para soporte multiplataforma (Windows/Linux)
init(autoreset=True)

# --- IMPORTES MODULARES ---
from command_handler import CommandHandler
from ai_config import configuracion_ia

class JarvisEngine:
    def __init__(self):
        """
        Inicializa Jarvis y sus variables configurables.
        """
        pygame.mixer.init()
        
        # --- CONFIGURACIÓN ---
        """
        CATALOGO DE VOCES RECOMENDADAS:
        - 'es-MX-JorgeNeural' (Hombre - Predeterminado)
        - 'es-MX-DaliaNeural' (Mujer)
        - 'es-CO-GonzaloNeural' (Hombre - Colombia)
        - 'es-AR-TomasNeural' (Hombre - Argentina)
        """
        self.voz_seleccionada = 'es-MX-JorgeNeural'
        self.palabras_activacion = [
            "jarvis", "café", "cafe", "despierta", "iarvis", "yaris", "yavis", "sharvis", "giarvis", "yarvis", "yarbiz"
        ]
        self.palabras_desactivacion = [
            "listo", "descansa", "silencio", "ya está", "calla", "callate", "lizto", "isto"
        ]
        
        # --- Variables de Estado y Archivos ---
        self.esta_dormido = False
        self.aplausos_activos = True  # Se puede desactivar con el comando "sin aplausos"
        self.archivo_temporal = "jarvis_voz.mp3"
        
        # --- Motor de Reconocimiento de Voz ---
        self.reconocedor = sr.Recognizer()
        
        # AJUSTES DE SENSIBILIDAD (Configuración vital para frases largas):
        # 1. pause_threshold: Segundos de silencio absoluto que Jarvis esperará antes de declarar que terminaste de hablar.
        self.reconocedor.pause_threshold = 1.5  
        
        # 2. phrase_threshold: Segundos mínimos de audio (voz) que deben detectarse para que se considere una frase válida.
        self.reconocedor.phrase_threshold = 0.3 
        
        # 3. non_speaking_duration: Duración del 'colchón' de silencio ambiental que se requiere antes de iniciar la captura.
        self.reconocedor.non_speaking_duration = 0.5

        # --- Inicialización de Módulos Inteligentes ---
        self.modo_ia_habilitado = configuracion_ia.verificar_y_configurar()
        self.manejador_de_comandos = CommandHandler(self)

    async def _generar_audio_asincrono(self, texto):
        comunicar = edge_tts.Communicate(texto, self.voz_seleccionada)
        await comunicar.save(self.archivo_temporal)

    def speak(self, mensaje_a_voz, mudo=False):
        """
        Muestra la respuesta en consola y, si no está en modo mudo, la reproduce por voz.
        """
        # Verde para Jarvis
        print(f"\n{Fore.GREEN}[JARVIS RESPONDE]: {mensaje_a_voz}")
        
        # Si el input vino por teclado (mudo=True), no reproducimos sonido
        if mudo:
            return

        # Limpieza de Markdown para la voz (evita que lea asteriscos, guiones bajos o almohadillas)
        texto_para_voz = re.sub(r'[*_#`~]', '', mensaje_a_voz)

        try:
            # 1. Generamos el audio neuronal con el texto limpio para una lectura fluida
            asyncio.run(self._generar_audio_asincrono(texto_para_voz))
            
            # 2. Preparamos el sistema de interrupción (solo si hay voz)
            self.interrumpido = False
            
            def callback_interrupcion(recognizer, audio):
                try:
                    texto = recognizer.recognize_google(audio, language="es-ES").lower()
                    if any(p in texto for p in self.palabras_desactivacion):
                        print("[SISTEMA]: Interrupción por voz detectada.")
                        self.interrumpido = True
                        pygame.mixer.music.stop()
                except: pass

            # Inicia el hilo de escucha en segundo plano
            stop_listening = self.reconocedor.listen_in_background(sr.Microphone(), callback_interrupcion, phrase_time_limit=2)
            
            # 3. Reproducción
            pygame.mixer.music.load(self.archivo_temporal)
            pygame.mixer.music.play()
            
            # 4. Espera a que termine o sea interrumpido
            while pygame.mixer.music.get_busy() and not self.interrumpido:
                pygame.time.Clock().tick(10)
            
            # Detiene el hilo de escucha
            stop_listening(wait_for_stop=False)
            
            # Descarga el archivo de audio
            pygame.mixer.music.unload()
            
        except Exception as error_audio:
            print(f"[ERROR AUDIO]: No se pudo reproducir: {error_audio}")

    def procesar_logica_entrada(self, texto_usuario, por_voz=False):
        """
        Punto central donde convergen la VOZ y el TEXTO.
        El parámetro 'por_voz' decide si la respuesta será hablada o solo escrita.
        """
        if not texto_usuario: return
        
        texto_limpio = texto_usuario.lower()
        mudo = not por_voz # Si NO es por voz, entonces mudo es True
        
        # --- LÓGICA DE ACTIVACIÓN / DESACTIVACIÓN ---
        ha_dicho_activacion = any(palabra in texto_limpio for palabra in self.palabras_activacion)
        
        # Si Jarvis está dormido, solo se despierta si se dice una palabra de activación
        if self.esta_dormido:
            if ha_dicho_activacion:
                self.esta_dormido = False
                self.speak("Sistemas activados. Dime qué necesitas.", mudo=mudo)
            return

        if any(palabra == texto_limpio or palabra in texto_limpio for palabra in self.palabras_desactivacion):
            self.esta_dormido = True
            self.speak("Entrando en modo de espera. Di Jarvis o Café para activarme.", mudo=mudo)
            return

        # --- PROCESAMIENTO NORMAL ---
        # Celeste/Cian para el usuario
        if por_voz:
            print(f"\n{Fore.CYAN}[VOZ]: '{texto_limpio}'")
        else:
            print(f"\n{Fore.CYAN}[TECLADO]: '{texto_limpio}'")

        # Ejecuta comandos locales o consulta a la IA
        if not self.manejador_de_comandos.ejecutar_comando_local(texto_limpio, mudo=mudo):
            self.manejador_de_comandos.procesar_consulta_ia(texto_limpio, mudo=mudo)

    def _hilo_detector_aplauso(self):
        """
        Corre en segundo plano de forma permanente (incluso si Jarvis está dormido).
        Detecta dos picos de energía rápidos (patrón de aplauso) y ejecuta la rutina configurada.
        Se puede pausar/reanudar con los comandos 'sin aplausos' / 'activar aplausos'.
        """
        try:
            import pyaudio
        except ImportError:
            print("[APLAUSO]: PyAudio no instalado. El detector de aplausos está desactivado.")
            return

        # --- Parámetros de detección ---
        CHUNK = 1024           # Muestras por lectura
        RATE = 44100           # Frecuencia de muestreo
        UMBRAL_ENERGIA = 20000 # Picos por encima de este valor se consideran un golpe
        VENTANA_APLAUSO = 0.8  # Segundos máximos entre dos golpes para contar como aplauso
        COOLDOWN = 2.0         # Segundos de espera tras detectar un aplauso (anti-spam)

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                         input=True, frames_per_buffer=CHUNK)

        print("[APLAUSO]: Detector iniciado. 👏 Dos aplausos = rutina de aplauso.")

        golpes = []          # Timestamps de cada pico detectado
        ultimo_aplauso = 0   # Timestamp del último aplauso procesado

        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)

                # Si los aplausos están desactivados, vaciamos golpes y no procesamos
                if not self.aplausos_activos:
                    golpes.clear()
                    time.sleep(0.1)
                    continue

                # Calculamos el pico máximo del fragmento de audio
                muestras = struct.unpack(f'{CHUNK}h', data)
                energia = max(abs(m) for m in muestras)

                ahora = time.time()

                if energia > UMBRAL_ENERGIA:
                    # Filtramos golpes demasiado seguidos (mismo aplauso captado dos veces)
                    if not golpes or (ahora - golpes[-1]) > 0.1:
                        golpes.append(ahora)

                # Limpiamos golpes viejos fuera de la ventana temporal
                golpes = [t for t in golpes if ahora - t <= VENTANA_APLAUSO]

                # ¡Dos golpes en la ventana = APLAUSO DETECTADO!
                if len(golpes) >= 2 and (ahora - ultimo_aplauso) > COOLDOWN:
                    golpes.clear()
                    ultimo_aplauso = ahora
                    print("\n[APLAUSO]: 👏 ¡Aplauso detectado! Ejecutando rutina...")
                    # Llamamos directamente al manejador, bypasseando el estado dormido
                    self.manejador_de_comandos.ejecutar_rutina_aplauso()

            except Exception as e:
                print(f"[APLAUSO ERROR]: {e}")
                time.sleep(0.5)

    def loop_hibrido(self, fuente_microfono):
        """
        Mantiene el micrófono en segundo plano y el teclado en primer plano.
        """
        print("\n>>> JARVIS HÍBRIDO - MODO CONSOLA ACTIVO")
        
        # Calibrar ruido
        with fuente_microfono as origen:
            self.reconocedor.adjust_for_ambient_noise(origen, duration=1)
        
        self.speak("Sistemas listos. Habla o escribe.")

        # --- HILO DE DETECCIÓN DE APLAUSOS (Siempre activo, ignora modo dormido) ---
        hilo_aplauso = threading.Thread(target=self._hilo_detector_aplauso, daemon=True)
        hilo_aplauso.start()

        # Hilo de Voz (Segunda plano)
        def _callback_voz(reconocedor, audio):
            try:
                frase = reconocedor.recognize_google(audio, language="es-ES").lower()
                self.procesar_logica_entrada(frase, por_voz=True)
            except: pass

        # Inicia el hilo de escucha en segundo plano
        self.reconocedor.listen_in_background(fuente_microfono, _callback_voz, phrase_time_limit=12)

        # Hilo de Texto (Primer plano)
        while True:
            try:
                label = "[DORMIDO]" if self.esta_dormido else "[ACTIVO]"
                entrada_teclado = input(f"\n{label} ESCRIBE >>> ")
                
                if entrada_teclado.strip():
                    self.procesar_logica_entrada(entrada_teclado, por_voz=False)
                    
            except (EOFError, KeyboardInterrupt): break

    # Prepara el micrófono
    def preparar_microfono(self):
        try:
            return sr.Microphone()
        except:
            print("[ALERTA]: Semántic Error - No se detectó micrófono. Modo solo texto.")
            return None

# Punto de entrada
if __name__ == "__main__":
    # Cambia al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    mi_jarvis = JarvisEngine()
    canal_microfono = mi_jarvis.preparar_microfono()
    
    try:
        if canal_microfono:
            mi_jarvis.loop_hibrido(canal_microfono)
        else:
            while True:
                texto = input("\n[TECLADO] >>> ")
                mi_jarvis.procesar_logica_entrada(texto, por_voz=False)
    except KeyboardInterrupt:
        print("\n[SISTEMA]: Sesión terminada.")
        if os.path.exists("jarvis_voz.mp3"):
            try: os.remove("jarvis_voz.mp3")
            except: pass
        sys.exit(0)
