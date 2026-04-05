import os
from dotenv import load_dotenv

# Cargamos las variables definidas en el archivo .env
load_dotenv()

class AIConfiguration:
    def __init__(self):
        """
        Constructor que carga las claves y las URLs de la IA.
        """
        # --- PROVEEDOR 1 (Principal) ---
        self.api_key_principal = os.getenv("API_KEY_IA_1")
        self.base_url_principal = os.getenv("BASE_URL_IA_1")
        self.modelo_ia_principal = os.getenv("MODEL_IA_1", "gemini-1.5-flash")
        
        # --- PROVEEDOR 2 (Respaldo/Groq) ---
        self.api_key_respaldo = os.getenv("API_KEY_IA_2")
        self.base_url_respaldo = os.getenv("BASE_URL_IA_2")
        self.modelo_ia_respaldo = os.getenv("MODEL_IA_2", "llama-3.3-70b-versatile")
        
        # Otros ajustes
        self.prompt_personalidad = os.getenv("PROMPT_PERSONALIDAD", "Eres Jarvis, un asistente de voz inteligente.")
        self.ia_esta_habilitada = False

    def verificar_y_configurar(self):
        # ... logic remains ...
        """
        Verifica el estado de las claves. Si no hay claves reales configuradas,
        se activa el 'Modo Limitado' y se notifica al usuario.
        """
        # Una clave se considera no cargada si es None, está vacía o tiene el texto del ejemplo
        claves_invalidas = [None, "", "tu_api_key_principal_aqui", "tu_api_key_respaldo_aqui"]
        
        if self.api_key_principal in claves_invalidas and self.api_key_respaldo in claves_invalidas:
            print("\n[ALERTA SISTEMA]: No se detectaron API Keys cargadas en el archivo .env.")
            print("[ADVERTENCIA]: El programa iniciará en MODO LIMITADO.")
            print("[ADVERTENCIA]: Solo estarán disponibles los comandos locales del sistema.")
            self.ia_esta_habilitada = False
            return False
        
        self.ia_esta_habilitada = True
        return True

    def obtener_clave_activa(self):
        """
        Retorna la clave principal si existe, de lo contrario la de respaldo.
        """
        if self.api_key_principal and "aqui" not in self.api_key_principal:
            return self.api_key_principal
        return self.api_key_respaldo

# Instancia global para ser accesible desde cualquier módulo
configuracion_ia = AIConfiguration()
