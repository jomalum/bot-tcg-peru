import os
import time
import datetime
import httpx
from threading import Thread
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = "https://www.plazavea.com.pe/coleccion-ultra-premium-tcg-30-aniversario-ingles-20711636/p"

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
                "content": "@here 🔄 **¡VOLVIÓ EL STOCK!** · Pokémon TCG / Coleccionables",
                "embeds": [{
                    "title": titulo,
                    "url": URL_PRODUCTO,
                    "description": descripcion,
                    "color": color,
                    "fields": [
                        {"name": "📦 Stock", "value": "🟢 Disponible", "inline": True},
                        {"name": "🏬 Tienda", "value": "Plaza Vea", "inline": True},
                        {"name": "🔗 Enlace Directo", "value": f"[Hacer clic aquí para ir a Plaza Vea]({URL_PRODUCTO})", "inline": False},
                        {"name": "📋 Código SKU", "value": f"`{SKU_PRODUCTO}`", "inline": True},
                        {"name": "🕒 Detectado", "value": obtener_hora_peru(), "inline": True}
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

# Prueba inicial para verificar comunicación
print("🚀 Enviando tarjeta de prueba a Discord...")
enviar_alerta_discord(
    "🛒 **Pokémon TCG 30 Aniversario UPC — ¡Disponible! (Prueba)**",
    f"¡El producto con SKU **{SKU_PRODUCTO}** ha vuelto a tener stock en Plaza Vea! Haz clic en el título o en el enlace de abajo para abrir la tienda al instante.",
    3066993,
    es_embed=True
)

def sniper_loop():
    print("🤖 Bot Sniper vigilando estrictamente el botón de agregar activo...")
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
                    
                    # 1. Verificamos que el botón de agregar exista explícitamente como activo
                    # Buscamos clases típicas de botones habilitados de compra en VTEX o la estructura del botón sin bloqueo
                    boton_activo = "add-to-cart-button" in html_texto or "buy-button" in html_texto or "agregar" in html_texto
                    
                    # 2. Buscamos exhaustivamente cualquier indicador de que está agotado o inactivo
                    esta_deshabilitado = (
                        "product-unavailable" in html_texto or
                        "out-of-stock" in html_texto or
                        "producto agotado" in html_texto or
                        "unavailable" in html_texto or
                        'class="add-to-cart-button ausgeschaltet"' in html_texto or
                        "disabled" in html_texto
                    )
                    
                    # La alerta solo salta si hay indicios de compra activos y CERO estados de agotado
                    if boton_activo and not esta_deshabilitado:
                        print("🚀 ¡BOTÓN DE AGREGAR HABILITADO Y STOCK REAL CONFIRMADO!")
                        enviar_alerta_discord(
                            "🛒 **Pokémon TCG 30 Aniversario UPC — ¡Disponible para Compra!**",
                            f"¡El botón de agregar está habilitado para el producto con SKU **{SKU_PRODUCTO}**! Haz clic en el enlace para comprar antes de que se agote.",
                            3066993,
                            es_embed=True
                        )
                        time.sleep(1800) # Pausa de 30 minutos tras una alerta real
                            
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
