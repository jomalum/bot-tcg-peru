import os
import time
import requests
from threading import Thread
from flask import Flask

# Servidor web para mantener Render despierto 24/7
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# Configuración
WEBHOOK_URL = "https://discord.com/api/webhooks/1558296831052611716/Qg74kXBmmQOCRI3Vh0PpGm3RKc7mYqifXnHzSz4JtLiDnJqidMfkawxadzOlRYSarNDM"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

def enviar_alerta_discord(titulo, descripcion, color):
    if not WEBHOOK_URL or WEBHOOK_URL == "TU_WEBHOOK_AQUI":
        print("❌ Error: Falta configurar el Webhook URL en el código.")
        return
    
    data = {
        "embeds": [{
            "title": titulo,
            "description": descripcion,
            "color": color,
            "footer": {"text": "Bot Sniper Jomasuss TCG"}
        }]
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=5)
        print(f"Respuesta de Discord: {response.status_code}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

def sniper_loop():
    print("🤖 Bot Sniper iniciado correctamente...")
    
    # Mensaje inicial directo a Discord al arrancar
    enviar_alerta_discord(
        "🟡 ¡BOT REINICIADO Y CONECTADO!", 
        f"El sniper ya está vigilando el producto con SKU: `{SKU_PRODUCTO}` en Plaza Vea.", 
        16776960
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        try:
            response = requests.get(URL_PRODUCTO, headers=headers, timeout=10)
            print(f"Código HTTP de la tienda: {response.status_code}")
            
            if response.status_code == 200:
                html_texto = response.text.lower()
                if "comprar" in html_texto or "agregar" in html_texto:
                    if "agotado" not in html_texto and "unavailable" not in html_texto:
                        print("🚀 ¡POSIBLE STOCK DETECTADO!")
                        enviar_alerta_discord(
                            "🟢 ¡ALERTA DE STOCK EN PLAZA VEA!", 
                            f"El producto SKU `{SKU_PRODUCTO}` muestra disponibilidad. ¡Revisa la web!", 
                            3066993
                        )
                        time.sleep(1800) # Pausa de 30 min
                        
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20) # Revisa cada 20 segundos

if __name__ == "__main__":
    # Arrancamos Flask en segundo plano
    t = Thread(target=run_web)
    t.start()
    
    # Ejecutamos el sniper en el hilo principal
    sniper_loop()
