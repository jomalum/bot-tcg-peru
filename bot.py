import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1560021358166024302/oPYRwURN2Sq_vbiUCpQ7O5Ycqd4SbReQFiA1I5WeKX7rOL_LMSlRoP4JceN1kWoXDMmc"

PRODUCTOS = [
    {
        "nombre": "Colección Ultra Premium TCG 30 Aniv. (UPC)",
        "url": "https://www.plazavea.com.pe/coleccion-ultra-premium-tcg-30-aniversario-ingles-20711636/p",
        "sku": "12603241",
        "max_qty": 5
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
        
        url_autocompra = f"https://www.plazavea.com.pe/checkout/cart/add?sku={prod_sku}&qty={max_qty}&seller=1"
        
        data = {
            "content": f"@here ⚡ **¡PRUEBA DE WEBHOOK Y AUTOCOMPRA!** ⚡",
            "embeds": [{
                "title": f"🚀 PRUEBA / ALERTA: {prod_nombre}",
                "url": url_autocompra,
                "description": f"Sistema activo. Enlace preparado para asegurar **{max_qty} unidades**.",
                "color": color,
                "fields": [
                    {"name": "📦 Cantidad Máxima", "value": f"🟢 {max_qty} Unidades", "inline": True},
                    {"name": "⚡ ENLACE DE AUTOCOMPRA", "value": f"[AÑADIR {max_qty} AL CARRITO]({url_autocompra})", "inline": False},
                    {"name": "🕒 Hora", "value": obtener_hora_peru(), "inline": True}
                ]
            }]
        }
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"👉 RESPUESTA DISCORD ({prod_nombre}) - Código: {response.status_code}", flush=True)
                
    except Exception as e:
        print(f"❌ Error en autocompra Discord: {e}", flush=True)

def sniper_loop():
    print("🤖 Bot de Detección y Autocompra iniciado correctamente...", flush=True)
    time.sleep(5)  # Pausa breve para asegurar que Flask esté listo
    
    # Mensaje de prueba inicial para validar Discord
    enviar_alerta_autocompra(
        "Sistema TCG (Inicio Estable)",
        "https://www.plazavea.com.pe",
        "12603241",
        1,
        3066993
    )

    while True:
        for prod in PRODUCTOS:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                with httpx.Client(http2=True, follow_redirects=True) as client:
                    response = client.get(prod["url"], headers=headers, timeout=10)
                    print(f"Revisando {prod['nombre']} - HTTP: {response.status_code}", flush=True)
                    
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
                            print(f"🚀 ¡STOCK DETECTADO PARA: {prod['nombre']}!", flush=True)
                            enviar_alerta_autocompra(prod["nombre"], prod["url"], prod["sku"], prod["max_qty"], 3066993)
                            time.sleep(1800)
                                
            except Exception as e:
                print(f"Error en escaneo de {prod['nombre']}: {e}", flush=True)
                
            time.sleep(10)
            
        time.sleep(15)

@app.route('/')
def home():
    return "Bot de Autocompra TCG Activo 24/7"

if __name__ == "__main__":
    # Iniciar el sniper en un hilo secundario daemon
    t = Thread(target=sniper_loop, daemon=True)
    t.start()
    
    # Iniciar Flask obligatorio para Render en el puerto asignado
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
