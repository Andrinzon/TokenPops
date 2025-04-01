import requests
from bs4 import BeautifulSoup
import json
import time
from telegram import Bot
from telegram.ext import Application, CommandHandler

# Configuración del bot de Telegram
TELEGRAM_TOKEN = "7463495309:AAFnWbMN8eYShhTt9UvygCD0TAFED-LuJhM"
CHAT_ID = "-1002516741524"  # Nuevo chat_id
bot = Bot(token=TELEGRAM_TOKEN)

# URL de la página de Binance que muestra las nuevas criptomonedas listadas
BINANCE_NEW_COINS_URL = "https://www.binance.com/es/altcoins/new"

# Archivo donde guardaremos las monedas detectadas previamente
DATA_FILE = "listed_coins.json"

def obtener_monedas_binance():
    """Obtiene la lista de nuevas monedas listadas en Binance desde la página web."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; YourBot/1.0; +http://yourdomain.com/bot)"
        }
        response = requests.get(BINANCE_NEW_COINS_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer los nombres de las nuevas criptomonedas listadas
        nuevas_monedas = set()
        for item in soup.find_all('div', class_='css-1ap5wc6'):
            nombre = item.find('div', class_='css-1ap5wc6').text.strip()
            nuevas_monedas.add(nombre)

        return nuevas_monedas

    except Exception as e:
        print(f"Error al obtener monedas de Binance: {e}")
        return set()

def cargar_monedas_guardadas():
    """Carga las monedas guardadas anteriormente."""
    try:
        with open(DATA_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_monedas(monedas):
    """Guarda la lista de monedas detectadas."""
    with open(DATA_FILE, "w") as file:
        json.dump(list(monedas), file)

def notificar_nueva_moneda(moneda):
    """Envía un mensaje a Telegram cuando se detecta una nueva moneda."""
    mensaje = f"🚀 Nueva moneda listada en Binance: {moneda}"
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensaje)
        print(mensaje)
    except Exception as e:
        print(f"Error al enviar mensaje a Telegram: {e}")

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
    await update.message.reply_text("✅ El bot está funcionando correctamente. ¡Te mantendré informado sobre nuevas monedas en Binance!")

def main():
    """Inicia el bot con el comando /start."""
    # Crea la instancia de la aplicación
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Comando /start
    application.add_handler(CommandHandler("start", start))

    # Inicia el bot
    application.run_polling()

    # Ejecuta la verificación de monedas en paralelo
    while True:
        verificar_nuevas_monedas()
        time.sleep(300)  # Espera 5 minutos antes de volver a verificar

if __name__ == "__main__":
    main()
