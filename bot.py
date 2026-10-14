import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"

# Lista de productos a vigilar (URL, nombre y SKU real de inventario)
PRODUCTOS = [
    {
        "nombre": "Colección Ultra Premium TCG 30 Aniv. (UPC)",
        "url": "https://www.plazavea.com.pe/coleccion-ultra-premium-tcg-30-aniversario-ingles-20711636/p",
        "sku": "12603241"
    },
    {
        "nombre": "Álbum Coleccionable TCG 30 Aniversario Inglés",
        "url": "https://www.plazavea.com.pe/album-coleccionable-tcg-30-aniversario-ingles-20711641/p",
        "sku": "12603174"
    }
]

def obtener_hora_peru():
    peru_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    return peru_time.strftime("%d/%m %H:%M:%S (Perú)")

def enviar_alerta_discord(prod_nombre, prod_url, prod_sku, color):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        url_carrito_directo = f"https://www.plazavea.com.pe/checkout/cart/add?sku={prod_sku}&qty=1&seller=1"
        
        data = {
            "content": f"@here 🔄 **¡STOCK DISPONIBLE EN PLAZA VEA!**",
            "embeds": [{
                "title": f"🛒 {prod_nombre}",
                "url": url_carrito_directo,
                "description": f"¡El producto **{prod_nombre}** tiene stock activo! Haz clic en el título o enlace para agregarlo al carrito de inmediato.",
                "color": color,
                "fields": [
                    {"name": "📦 Stock", "value": "🟢 Disponible", "inline": True},
                    {"name": "🏬 Tienda", "value": "Plaza Vea", "inline": True},
                    {"name": "🛒 Enlace Directo al Carrito", "value": f"[Añadir al Carrito con 1 Clic]({url_carrito_directo})", "inline": False},
                    {"name": "🔗 Ver Página", "value": f"[Ir a la tienda]({prod_url})", "inline": False},
                    {"name": "📋 Código SKU", "value": f"`{prod_sku}`", "inline": True},
                    {"name": "🕒 Detectado", "value": obtener_hora_peru(), "inline": True}
                ],
                "footer": {
                    "text": "Jomasuss TCG Multi-Sniper"
                }
            }]
        }
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"Respuesta de Discord ({prod_nombre}) - Código: {response.status_code}")
        
        if response.status_code == 429:
            print("⚠️ Discord rate limit (429). Pausando 5 segundos...")
            time.sleep(5)
            
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

# Prueba de arranque
time.sleep(3)
print("🚀 Enviando tarjeta de prueba multi-producto a Discord...")
enviar_alerta_discord(
    "Sistema Multi-Sniper TCG Activo",
    "https://www.plazavea.com.pe",
    "000000",
    3066993
)

def sniper_loop():
    print("🤖 Bot Multi-Sniper vigilando la lista de productos...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        for prod in PRODUCTOS:
            try:
                with httpx.Client(http2=True, follow_redirects=True) as client:
                    response = client.get(prod["url"], headers=headers, timeout=10)
                    print(f"Revisando {prod['nombre']} - HTTP: {response.status_code}")
                    
                    if response.status_code == 200:
                        html_texto = response.text.lower()
                        
                        boton_activo = "agregar" in html_texto or "comprar" in html_texto
                        esta_deshabilitado = (
                            "product-unavailable" in html_texto or
                            "out-of-stock" in html_texto or
                            "producto agotado" in html_texto or
                            "unavailable" in html_texto or
                            "disabled" in html_texto
                        )
                        
                        if boton_activo and not esta_deshabilitado:
                            print(f"🚀 ¡STOCK DETECTADO PARA: {prod['nombre']}!")
                            enviar_alerta_discord(prod["nombre"], prod["url"], prod["sku"], 3066993)
                            time.sleep(300) # Pausa específica para este producto si hay stock
                            
            except Exception as e:
                print(f"Error revisando {prod['nombre']}: {e}")
                
            time.sleep(10) # Breve pausa entre cada producto para no saturar
            
        time.sleep(15) # Pausa antes de repetir la ronda completa

@app.route('/')
def home():
    return "Bot Multi-Sniper TCG Activo 24/7"

if __name__ == "__main__":
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
