import os
import httpx
import asyncio
from datetime import datetime
from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# Pega tu Webhook de Discord aquí entre las comillas
WEBHOOK_URL = "https://discord.com/api/webhooks/1558296831052611716/Qg74kXBmmQOCRI3Vh0PpGm3RKc7mYqifXnHzSz4JtLiDnJqidMfkawxadzOlRYSarNDM"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

async def enviar_alerta_discord(titulo, descripcion, color):
    data = {
        "embeds": [{
            "title": titulo,
            "description": descripcion,
            "color": color,
            "footer": {"text": f"Hora Perú: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"}
        }]
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(WEBHOOK_URL, json=data)
            print(f"Respuesta de Discord: {response.status_code}")
        except Exception as e:
            print(f"Error enviando a Discord: {e}")

async def sniper_loop():
    print("🤖 Bot Sniper iniciado...")
    
    await enviar_alerta_discord(
        "🚨 ¡BOT REINICIADO Y CONECTADO!", 
        f"El sniper está vigilando el producto con SKU: `{SKU_PRODUCTO}`.", 
        16776960
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
        while True:
            try:
                response = await client.get(URL_PRODUCTO, headers=headers, timeout=10.0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Código HTTP de la tienda: {response.status_code}")
                
                if response.status_code == 200:
                    html_texto = response.text.lower()
                    if "comprar" in html_texto or "agregar" in html_texto:
                        if "agotado" not in html_texto and "unavailable" not in html_texto:
                            print("🚀 ¡POSIBLE STOCK DETECTADO!")
                            await enviar_alerta_discord(
                                "🟢 ¡ALERTA DE STOCK EN PLAZA VEA!", 
                                f"El producto `{SKU_PRODUCTO}` muestra botones de compra activos. ¡Revisa rápido la web!", 
                                3066993
                            )
                            await asyncio.sleep(1800)
                
            except Exception as e:
                print(f"Error en la petición web: {e}")
                
            await asyncio.sleep(20)

def iniciar_bot():
    asyncio.run(sniper_loop())

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    iniciar_bot()
