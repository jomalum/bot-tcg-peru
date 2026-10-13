import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
URL_PRODUCTO = "https://www.plazavea.com.pe/coleccion-ultra-premium-tcg-30-aniversario-ingles-20711636/p"
SKU_PRODUCTO = "12603241" # SKU real de la UPC obtenido del código fuente

URL_CARRITO_DIRECTO = f"https://www.plazavea.com.pe/checkout/cart/add?sku={SKU_PRODUCTO}&qty=1&seller=1"

def obtener_hora_peru():
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
                "content": "@here 🔄 **¡ALERTA DE STOCK - UPC!** · Pokémon TCG",
                "embeds": [{
                    "title": titulo,
                    "url": URL_CARRITO_DIRECTO,
                    "description": descripcion,
                    "color": color,
                    "fields": [
                        {"name": "📦 Stock", "value": "🟢 Disponible", "inline": True},
                        {"name": "🏬 Tienda", "value": "Plaza Vea", "inline": True},
                        {"name": "🛒 Enlace Directo al Carrito", "value": f"[Añadir UPC al Carrito con 1 Clic]({URL_CARRITO_DIRECTO})", "inline": False},
                        {"name": "🔗 Ver Página del Producto", "value": f"[Ir a la tienda]({URL_PRODUCTO})", "inline": False},
                        {"name": "📋 Código SKU", "value": f"`{SKU_PRODUCTO}`", "inline": True},
                        {"name": "🕒 Detectado", "value": obtener_hora_peru(), "inline": True}
                    ],
                    "footer": {
                        "text": "Jomasuss TCG Sniper · UPC Correcta"
                    }
                }]
            }
        else:
            data = {"content": titulo}
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"Respuesta de Discord - Código: {response.status_code}")
        
        # Si Discord nos da rate limit (429), esperamos unos segundos
        if response.status_code == 429:
            print("⚠️ Discord rate limit (429) alcanzado. Pausando 5 segundos...")
            time.sleep(5)
            
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

# Pausa breve al arrancar para evitar saturar el webhook con el primer despliegue
time.sleep(3)
print("🚀 Enviando tarjeta de prueba a Discord con el SKU correcto de la UPC...")
enviar_alerta_discord(
    "🛒 **Colección Ultra Premium TCG 30 Aniv. — ¡Sistema Activo!**",
    f"¡El bot se ha conectado correctamente con el SKU real **{SKU_PRODUCTO}**! Vigilando stock en tiempo real.",
    3066993,
    es_embed=True
)

def sniper_loop():
    print("🤖 Bot Sniper vigilando la UPC de la Colección Ultra Premium...")
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
                    
                    boton_activo = "agregar" in html_texto or "comprar" in html_texto
                    esta_deshabilitado = (
                        "product-unavailable" in html_texto or
                        "out-of-stock" in html_texto or
                        "producto agotado" in html_texto or
                        "unavailable" in html_texto or
                        "disabled" in html_texto
                    )
                    
                    if boton_activo and not esta_deshabilitado:
                        print("🚀 ¡STOCK REAL Y BOTÓN HABILITADO CONFIRMADO PARA LA UPC!")
                        enviar_alerta_discord(
                            "🛒 **Colección Ultra Premium TCG 30 Aniv. — ¡Disponible para Compra!**",
                            f"¡La UPC con SKU **{SKU_PRODUCTO}** tiene stock activo! Haz clic abajo para añadirla al carrito al instante.",
                            3066993,
                            es_embed=True
                        )
                        time.sleep(1800)
                            
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20)

@app.route('/')
def home():
    return "Bot Sniper UPC TCG Activo 24/7"

if __name__ == "__main__":
    t = Thread(target=sniper_loop)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
