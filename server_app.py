from flask import Flask, request, jsonify
import sys
import os
from colorama import init, Fore, Style

# INICIALIZACIÓN: Activamos colores para la consola (Indispensable para Termux/Linux)
init(autoreset=True)

# CONFIGURACIÓN DE RUTAS
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from command_handler import CommandHandler
    from ai_config import configuracion_ia
    print(f"{Fore.GREEN}[LOG]: Motores de inteligencia cargados.")
except Exception as e:
    print(f"{Fore.RED}[ERROR]: Fallo crítico al cargar módulos: {e}")
    sys.exit(1)

app = Flask("Jarvis Remote Server")

# Clase TTS silenciosa para el servidor (solo registro visual)
class SilentTTS:
    def speak(self, texto, mudo=False):
        """Muestra en la consola física lo que Jarvis está pensando."""
        print(f"\n{Fore.GREEN}[PENSAMIENTO JARVIS]: {texto}")

# Inicialización del cerebro
print(f"{Fore.YELLOW}[LOG]: Inicializando controlador heurístico...")
jarvis_brain = CommandHandler(SilentTTS())

@app.route("/consultar", methods=["POST"])
def consultar():
    """Procesador de órdenes externas por red."""
    data = request.json
    if not data or 'mensaje' not in data:
        return jsonify({"error": "Falta el campo 'mensaje'"}), 400
    
    mensaje = data['mensaje']
    print(f"\n{Fore.CYAN}[REMOTO]: Petición entrante -> '{mensaje}'")
    
    try:
        # 1. Comandos físicos (Solo si es Windows)
        if jarvis_brain.ejecutar_comando_local(mensaje, mudo=True):
            print(f"{Fore.YELLOW}[INFO]: Comando físico ejecutado en el servidor remoto.")
            return jsonify({"respuesta": "[Orden física ejecutada en el servidor]"})
        
        # 2. IA pura
        respuesta_ia = jarvis_brain.procesar_consulta_ia_remota(mensaje)
        # Mostramos la respuesta también en la consola del servidor
        print(f"{Fore.GREEN}[RESPUESTA]: Enviando resultado al cliente.")
        return jsonify({"respuesta": respuesta_ia})
        
    except Exception as e:
        print(f"{Fore.RED}[ERROR]: Fallo al procesar la red: {e}")
        return jsonify({"respuesta": "Sesión de IA interrumpida por un error interno."}), 500

if __name__ == "__main__":
    print(f"\n{Fore.WHITE}==========================================")
    print(f"{Fore.CYAN}  SERVIDOR JARVIS ACTIVO (Puerto: 8000)")
    print(f"{Fore.WHITE}==========================================\n")
    # Escuchamos a cualquier dispositivo de la red local
    app.run(host="0.0.0.0", port=8000, debug=False)
