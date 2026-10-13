import os
import time
import httpx
from flask import Flask

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1559386997674737814/H_KhSDuWmEhp9KqHDpHKJ3zSgG1z3gSQfDrh7RO720uCydDd-7aCig6_a1_-lVC39W_h"
SKU_PRODUCTO = "20711636"
URL_PRODUCTO = f"https://www.plazavea.com.pe/{SKU_PRODUCTO}/p"

def enviar_alerta_discord(mensaje):
    try:
        # Encabezado obligatorio exigido por Discord para evitar el bloqueo de Cloudflare
        headers = {
            "User-Agent": "DiscordBot (https://discord.com, 1.0)",
            "Content-Type": "application/json"
        }
        response = httpx.post(WEBHOOK_URL, json={"content": mensaje}, headers=headers, timeout=5)
        print(f"Respuesta de Discord - Código: {response.status_code} - Texto: {response.text}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

print("🚀 Ejecutando alerta de prueba inicial hacia Discord...")
enviar_alerta_discord("🟡 **¡BOT REINICIADO Y CONECTADO!** El sniper ya está vigilando el SKU: `" + SKU_PRODUCTO + "` en Plaza Vea.")

@app.route('/')
def home():
    return "Bot Sniper TCG Activo 24/7"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
