import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

def obtener_hora_peru():
    # Calcula la hora actual en Perú (UTC-5)
    peru_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    return peru_time.strftime("%d/%m %H:%M:%S (Perú)")

def enviar_alerta_discord(titulo, descripcion, color, es_embed=True):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        if es_embed:
            data = {
                "content": "@here 🔄 **¡VOLVIÓ EL STOCK!** · Pokémon TCG / Coleccionables",
                "embeds": [{
                    "title": titulo,
                    "url": URL_PRODUCTO,
                    "description": descripcion,
                    "color": color,
                    "fields": [
                        {"name": "📦 Stock", "value": "🟢 Disponible", "inline": True},
                        {"name": "🏬 Tienda", "value": "Plaza Vea", "inline": True},
                        {"name": "📋 Código SKU", "value": f"`{SKU_PRODUCTO}`", "inline": False},
                        {"name": "🕒 Detectado", "value": obtener_hora_peru(), "inline": False}
                    ],
                    "footer": {
                        "text": "Jomasuss TCG Sniper · Stock y precios sujetos a cambios"
                    }
                }]
            }
        else:
            data = {"content": titulo}
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"Respuesta de Discord - Código: {response.status_code}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

def sniper_loop():
    print("🤖 Bot Sniper en espera de seguridad (20s)...")
    time.sleep(20)
    
    print("🤖 Bot Sniper iniciado y vigilando stock...")
    enviar_alerta_discord(
        "🟡 **¡BOT REINICIADO Y CONECTADO!**", 
        f"El sniper ya se encuentra vigilando el producto con SKU `{SKU_PRODUCTO}` en Plaza Vea 24/7.", 
        16776960, 
        es_embed=False
    )
    
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
                                "🛒 **¡Disponible para Compra!**",
                                f"¡El producto con SKU **{SKU_PRODUCTO}** ha vuelto a tener stock en Plaza Vea! Haz clic en el título para ir directo al producto.",
                                3066993, # Color verde brillante estilo tarjeta
                                es_embed=True
                            )
                            time.sleep(1800) # Pausa de 30 minutos tras una alerta
                            
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20) # Revisa cada 20 segundos

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

if __name__ == "__main__":
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
