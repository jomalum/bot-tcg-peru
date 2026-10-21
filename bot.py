import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1560021358166024302/oPYRwURN2Sq_vbiUCpQ7O5Ycqd4SbReQFiA1I5WeKX7rOL_LMSlRoP4JceN1kWoXDMmc"

# Lista de productos vigilados con cantidad máxima de compra deseada
PRODUCTOS = [
    {
        "nombre": "Colección Ultra Premium TCG 30 Aniv. (UPC)",
        "url": "https://www.plazavea.com.pe/coleccion-ultra-premium-tcg-30-aniversario-ingles-20711636/p",
        "sku": "12603241",
        "max_qty": 5  # Stock máximo permitido o deseado por compra
    },
    {
        "nombre": "Álbum Coleccionable TCG 30 Aniversario Inglés",
        "url": "https://www.plazavea.com.pe/album-coleccionable-tcg-30-aniversario-ingles-20711641/p",
        "sku": "12603174",
        "max_qty": 10
    },
    {
        "nombre": "Sobre Cartas Coleccionables Pokémon TCG 30 Aniv.",
        "url": "https://www.plazavea.com.pe/sobre-cartas-coleccionables-pokemon-tcg-30%C2%BA-aniversario-ingles-20714698/p",
        "sku": "12613439",
        "max_qty": 20
    }
]

def obtener_hora_peru():
    peru_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    return peru_time.strftime("%d/%m %H:%M:%S (Perú)")

def enviar_alerta_autocompra(prod_nombre, prod_url, prod_sku, max_qty, color):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        
        # Enlace optimizado de autocompra directa inyectando el stock máximo configurado
        url_autocompra = f"https://www.plazavea.com.pe/checkout/cart/add?sku={prod_sku}&qty={max_qty}&seller=1"
        
        data = {
            "content": f"@here ⚡ **¡AUTOCOMPRA DISPONIBLE - STOCK MÁXIMO ACTIVADO!** ⚡",
            "embeds": [{
                "title": f"🚀 AUTOCOMPRA: {prod_nombre}",
                "url": url_autocompra,
                "description": f"¡Stock detectado! El bot ha preparado el enlace directo para asegurar **{max_qty} unidades** al instante.",
                "color": color,
                "fields": [
                    {"name": "📦 Cantidad Máxima", "value": f"🟢 {max_qty} Unidades", "inline": True},
                    {"name": "🏬 Tienda", "value": "Plaza Vea", "inline": True},
                    {"name": "⚡ ENLACE DE AUTOCOMPRA DIRECTA", "value": f"[¡AÑADIR {max_qty} AL CARRITO A 1 CLIC!]({url_autocompra})", "inline": False},
                    {"name": "🔗 Página del Producto", "value": f"[Ver web oficial]({prod_url})", "inline": False},
                    {"name": "📋 SKU", "value": f"`{prod_sku}`", "inline": True},
                    {"name": "🕒 Hora", "value": obtener_hora_peru(), "inline": True}
                ],
                "footer": {
                    "text": "Jomasuss TCG Auto-Sniper & Checkout System"
                }
            }]
        }
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"Alerta de autocompra enviada ({prod_nombre}) - Código: {response.status_code}")
                
    except Exception as e:
        print(f"Error en autocompra Discord: {e}")

def sniper_loop():
    print("🤖 Bot de Detección y Autocompra a 1 Click iniciado...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Mensaje de prueba inicial para verificar el webhook privado
    enviar_alerta_autocompra(
        "Sistema de Autocompra TCG (Prueba)",
        "https://www.plazavea.com.pe",
        "12603241",
        1,
        3066993
    )

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
                            print(f"🚀 ¡STOCK Y AUTOCOMPRA LISTOS PARA: {prod['nombre']}!")
                            enviar_alerta_autocompra(prod["nombre"], prod["url"], prod["sku"], prod["max_qty"], 3066993)
                            time.sleep(1800) # Pausa para evitar spam tras hallar stock
                                
            except Exception as e:
                print(f"Error en escaneo de {prod['nombre']}: {e}")
                
            time.sleep(10)
            
        time.sleep(15)

@app.route('/')
def home():
    return "Bot de Autocompra TCG Activo 24/7"

if __name__ == "__main__":
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
