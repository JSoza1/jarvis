import requests
import json

"""
=============================================================================
CENTRAL DE CONEXIONES IA - JARVIS
=============================================================================
Este archivo contiene la lógica técnica para hablar con cada proveedor de IA
sin usar sus librerías oficiales (SDKs). Usamos 'Requests' para que sea
ligero y funcione en cualquier lugar, como Termux o Windows.
=============================================================================
"""

def consultar_gemini(api_key, modelo, prompt_sistema, prompt_usuario):
    """
    CONEXIÓN CON GOOGLE GEMINI (Vía REST)
    """
    # 1. Construimos la URL con el modelo elegido y nuestra llave API secreta
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    
    # 2. Creamos el 'paquete' de datos (JSON) que Google espera recibir.
    #    Google usa una estructura de 'contents' y 'parts'.
    payload = {
        "contents": [
            {
                "parts": [
                    # Combinamos la personalidad (sistema) con la pregunta del usuario
                    {"text": f"{prompt_sistema}\nUsuario: {prompt_usuario}"}
                ]
            }
        ]
    }
    
    # 3. Enviamos la petición POST y esperamos máximo 15 segundos
    res = requests.post(url, json=payload, timeout=15)
    
    # 4. Si la respuesta no es 200 (OK), lanzamos un error para que Jarvis lo sepa
    res.raise_for_status()
    
    # 5. Convertimos la respuesta de texto a un diccionario de Python
    data = res.json()
    
    # 6. Navegamos por el JSON para sacar solo el texto de la respuesta
    if 'candidates' in data and data['candidates']:
        # 'candidates' -> [0] -> 'content' -> 'parts' -> [0] -> 'text'
        return data['candidates'][0]['content']['parts'][0]['text']
    
    return "Google no devolvió ninguna respuesta válida."

def consultar_groq(api_key, modelo, prompt_sistema, prompt_usuario):
    """
    CONEXIÓN CON GROQ (Vía REST - Compatible con OpenAI)
    """
    # 1. URL estándar de chat completions de Groq
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # 2. En las cabeceras (headers) mandamos el token de seguridad (Bearer)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 3. Groq usa el estándar de 'messages' con roles (system/user)
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt_sistema}, # Quién es Jarvis
            {"role": "user", "content": prompt_usuario}    # Qué dijo el usuario
        ],
        "max_tokens": 250 # Límite de palabras para no gastar cuota de más
    }
    
    # 4. Enviamos la petición con cabeceras y datos
    res = requests.post(url, headers=headers, json=payload, timeout=15)
    res.raise_for_status()
    
    # 5. Procesamos la respuesta JSON
    data = res.json()
    
    # 6. Sacamos el contenido del primer mensaje de la respuesta
    #    choices -> [0] -> 'message' -> 'content'
    return data['choices'][0]['message']['content']

def consultar_openai(api_key, base_url, modelo, prompt_sistema, prompt_usuario):
    """
    CONEXIÓN CON OPENAI O COMPATIBLES (Vía REST)
    """
    # 1. Si no hay una URL personalizada, usamos la oficial de OpenAI
    base = base_url if base_url else "https://api.openai.com/v1"
    
    # 2. Nos aseguramos de que la URL termine en /chat/completions
    url = f"{base.rstrip('/')}/chat/completions"
    
    # 3. Cabeceras de seguridad
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 4. Estructura estándar de mensajes
    payload = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        "max_tokens": 250
    }
    
    # 5. Enviamos y validamos la conexión
    res = requests.post(url, headers=headers, json=payload, timeout=15)
    res.raise_for_status()
    
    # 6. Extraemos el texto final
    data = res.json()
    return data['choices'][0]['message']['content']
