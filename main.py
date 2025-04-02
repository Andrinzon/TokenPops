import requests
import json
import time
from telegram import Bot
from telegram.ext import Application, CommandHandler

# Configuración del bot de Telegram
TELEGRAM_TOKEN = "7463495309:AAFnWbMN8eYShhTt9UvygCD0TAFED-LuJhM"
CHAT_ID = "-1002516741524"  # Grupo o usuario donde se enviarán las alertas
bot = Bot(token=TELEGRAM_TOKEN)

# API de Binance para obtener los pares de trading disponibles
BINANCE_API_URL = "https://api.binance.com/api/v3/exchangeInfo"

# Archivo donde guardaremos las monedas detectadas previamente
DATA_FILE = "listed_coins.json"

def obtener_monedas_binance():
    """Obtiene la lista de criptomonedas disponibles en Binance desde la API."""
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()

        # Extraer los símbolos de las monedas listadas en Binance
        monedas = set()
        for symbol in data["symbols"]:
            base_asset = symbol["baseAsset"]  # Ejemplo: BTC, ETH, SOL
            monedas.add(base_asset)

        return monedas

    except Exception as e:
        print(f"❌ Error al obtener monedas de Binance: {e}")
        return set()

def cargar_monedas_guardadas():
    """Carga la lista de monedas guardadas previamente."""
    try:
        with open(DATA_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_monedas(monedas):
    """Guarda la lista actual de monedas en Binance."""
    with open(DATA_FILE, "w") as file:
        json.dump(list(monedas), file)

def notificar_nueva_moneda(moneda):
    """Envía un mensaje a Telegram cuando se detecta una nueva moneda listada."""
    mensaje = f"🚀 *Nueva moneda listada en Binance:* `{moneda}`"
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")
        print(mensaje)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

def verificar_nuevas_monedas():
    """Verifica si hay nuevas monedas listadas en Binance."""
    print("🔍 Verificando nuevas monedas en Binance...")

    monedas_actuales = obtener_monedas_binance()
    monedas_guardadas = cargar_monedas_guardadas()

    nuevas_monedas = monedas_actuales - monedas_guardadas

    if nuevas_monedas:
        for moneda in nuevas_monedas:
            notificar_nueva_moneda(moneda)
        guardar_monedas(monedas_actuales)
    else:
        print("✅ No hay nuevas monedas listadas en Binance.")

async def start(update, context):
    """Comando /start para verificar si el bot está funcionando."""
    await update.message.reply_text("✅ *El bot está funcionando correctamente.*\nTe notificaré cuando haya nuevas monedas listadas en Binance.", parse_mode="Markdown")

def main():
    """Inicia el bot de Telegram y ejecuta la verificación en un bucle infinito."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

    while True:
        verificar_nuevas_monedas()
        time.sleep(300)  # Verifica cada 5 minutos

if __name__ == "__main__":
    main()
