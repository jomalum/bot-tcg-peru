import os
import time
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

def enviar_alerta_discord(mensaje):
    try:
        # Usamos parámetros planos y directos
        response = httpx.post(WEBHOOK_URL, data={"content": mensaje}, timeout=5)
        print(f"Respuesta de Discord - Código: {response.status_code} - Contenido: {response.text}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

def sniper_loop():
    print("🤖 Bot Sniper iniciado en segundo plano...")
    time.sleep(3)
    
    # Mensaje de prueba directo al arrancar
    enviar_alerta_discord("¡Hola! El bot sniper de Jomasuss TCG se ha conectado correctamente.")
    
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
                            enviar_alerta_discord(f"¡ATENCIÓN! El producto SKU {SKU_PRODUCTO} muestra disponibilidad en Plaza Vea.")
                            time.sleep(1800)
                            
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20)

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

if __name__ == "__main__":
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
