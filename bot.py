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

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
# Usamos el endpoint de simulación de stock de VTEX (Plaza Vea)
API_SIMULATION_URL = "https://www.plazavea.com.pe/api/checkout/pub/orderForm/simulation?sc=1"
SKU_PRODUCTO = "20711636"

async def enviar_alerta_discord(titulo, descripcion, color):
    data = {
        "embeds": [{
            "title": titulo,
            "description": descripcion,
            "color": color,
            "footer": {"text": f"Detectado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} (Perú)"}
        }]
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(WEBHOOK_URL, json=data)
        except Exception as e:
            print(f"Error enviando a Discord: {e}")

async def sniper_loop():
    print("🤖 Bot Sniper (Modo Simulación) iniciado en la nube 24/7...")
    await enviar_alerta_discord(
        "🟡 ¡BOT RECONFIGURADO!", 
        f"El sniper ahora monitorea el SKU `{SKU_PRODUCTO}` mediante simulación de stock.", 
        16776960
    )
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "items": [{"id": SKU_PRODUCTO, "quantity": 1, "seller": "1"}]
    }

    async with httpx.AsyncClient(http2=True) as client:
        while True:
            try:
                response = await client.post(API_SIMULATION_URL, json=payload, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    items_encontrados = data.get("items", [])
                    
                    if items_encontrados:
                        # Verificamos si la disponibilidad es mayor a 0
                        # En VTEX, si hay stock, suele retornar el precio y disponibilidad
                        availability = items_encontrados[0].get("availability")
                        list_price = items_encontrados[0].get("listPrice", 0)
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Respuesta OK - Disponibilidad: {availability}")
                        
                        # Si el producto tiene stock (en VTEX suele venir como "available" o con precio > 0)
                        if list_price > 0 or availability:
                            print("🚀 ¡STOCK DETECTADO!")
                            await enviar_alerta_discord(
                                "🟢 ¡STOCK DISPONIBLE DETECTADO!", 
                                f"El SKU `{SKU_PRODUCTO}` tiene stock activo en Plaza Vea. ¡Corre a comprar!", 
                                3066993
                            )
                            await asyncio.sleep(1800) # Espera 30 min para no spamear
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sin stock en la simulación.")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Código HTTP inesperado: {response.status_code}")
                    
            except Exception as e:
                print(f"Error en la petición: {e}")
                
            await asyncio.sleep(10) # Revisa cada 10 segundos

def iniciar_bot():
    asyncio.run(sniper_loop())

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    iniciar_bot()
