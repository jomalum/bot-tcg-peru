import os
import time
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

# Tu Webhook oficial y activo de Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

def enviar_alerta_discord(mensaje):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        response = httpx.post(WEBHOOK_URL, json={"content": mensaje}, headers=headers, timeout=5)
        print(f"Respuesta de Discord - Código: {response.status_code}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

def sniper_loop():
    # Pequeña pausa para asegurar estabilidad al arrancar en la nube
    print("🤖 Bot Sniper en espera de seguridad (20s)...")
    time.sleep(20)
    
    print("🤖 Bot Sniper iniciado y vigilando stock...")
    enviar_alerta_discord("🟡 **¡BOT REINICIADO Y CONECTADO!** El sniper ya está vigilando el SKU: `" + SKU_PRODUCTO + "` en Plaza Vea.")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        try:
            with httpx.Client(http2=True, follow_redirects=True) as client:
                response = client.get(URL_PRODUCTO, headers=headers, timeout=10)
                print(f"Código HTTP de la tienda: {response.status_code}")
                
                if response.status_code == 200:
                    html_texto = response.text.lower()
                    if "comprar" in html_texto or "agregar" in html_texto:
                        if "agotado" not in html_texto and "unavailable" not in html_texto:
                            print("🚀 ¡POSIBLE STOCK DETECTADO!")
                            enviar_alerta_discord(
                                "🟢 **¡ALERTA DE STOCK EN PLAZA VEA!** El producto SKU `" + SKU_PRODUCTO + "` muestra disponibilidad. ¡Corre a revisar la web!"
                            )
                            time.sleep(1800) # Pausa de 30 min si encuentra stock
                            
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20) # Revisa cada 20 segundos

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

if __name__ == "__main__":
    # Arrancamos el sniper en segundo plano para liberar el hilo principal del servidor web
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
