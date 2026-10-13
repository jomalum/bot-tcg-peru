
                
                if response.status_code == 200:
                    html_texto = response.text.lower()
                    if "comprar" in html_texto or "agregar" in html_texto:
                        if "agotado" not in html_texto and "unavailable" not in html_texto:
                            print("🚀 ¡POSIBLE STOCK DETECTADO!")
                            enviar_alerta_discord(
                                "🟢 **¡ALERTA DE STOCK EN PLAZA VEA!** El producto SKU `" + SKU_PRODUCTO + "` muestra disponibilidad. ¡Corre a revisar la web!"
                            )
                            time.sleep(1800) # Pausa de 30 min
                            
        except Exception as e:
            print(f"Error en la petición web: {e}")
            
        time.sleep(20) # Revisa cada 20 segundos

if __name__ == "__main__":
    # 1. Arrancamos Flask en segundo plano para que Render no cierre el servicio
    web_thread = Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()
    
    # 2. Ejecutamos el sniper directamente en el hilo principal
    sniper_loop()
