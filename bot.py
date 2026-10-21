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
                "title": f"🚀 PRUEBA: {prod_nombre}",
                "url": url_autocompra,
                "description": f"Mensaje de prueba del sistema para verificar canal privado.",
                "color": color,
                "fields": [
                    {"name": "📦 Cantidad", "value": f"🟢 {max_qty} Unidades", "inline": True},
                    {"name": "⚡ ENLACE", "value": f"[AÑADIR AL CARRITO]({url_autocompra})", "inline": False}
                ]
            }]
        }
            
        response = httpx.post(WEBHOOK_URL, json=data, headers=headers, timeout=5)
        print(f"👉 RESPUESTA DISCORD ({prod_nombre}) - Código: {response.status_code} - Respuesta: {response.text}", flush=True)
                
    except Exception as e:
        print(f"❌ Error crítico en autocompra Discord: {e}", flush=True)
