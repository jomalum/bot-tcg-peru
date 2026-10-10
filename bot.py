import os
import httpx
import asyncio
from datetime import datetime

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
API_CART_URL = "https://www.plazavea.com.pe/api/checkout/pub/orderForm/items"
SKU_PRODUCTO = "20711641" # El código de tu producto

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
    print("🤖 Bot Sniper iniciado en la nube 24/7...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    
    payload = {
        "orderItems": [{"id": SKU_PRODUCTO, "quantity": 1, "seller": "1"}]
    }

    async with httpx.AsyncClient(http2=True) as client:
        while True:
            try:
                response = await client.post(API_CART_URL, json=payload, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    print("🚀 ¡ITEM INYECTADO AL CARRITO!")
                    await enviar_alerta_discord(
                        "🟢 ¡PRODUCTO AÑADIDO AL CARRITO!", 
                        f"El bot interceptó el stock del SKU: `{SKU_PRODUCTO}` y lo cargó con éxito.", 
                        3066993
                    )
                    await asyncio.sleep(3600) 
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sin stock (Código: {response.status_code})")
                    
            except Exception as e:
                print(f"Error en la petición: {e}")
                
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(sniper_loop())
