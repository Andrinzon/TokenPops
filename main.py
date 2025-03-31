import asyncio
import requests
from bs4 import BeautifulSoup
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configuración del bot de Telegram
TELEGRAM_TOKEN = "7463495309:AAFnWbMN8eYShhTt9UvygCD0TAFED-LuJhM"
BINANCE_NEW_COINS_URL = "https://www.binance.com/es/altcoins/new"

DATA_FILE = "listed_coins.json"
USERS_FILE = "registered_users.json"

def obtener_monedas_binance():
    """Obtiene la lista de nuevas monedas listadas en Binance."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(BINANCE_NEW_COINS_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        nuevas_monedas = set()
        for item in soup.find_all('div', class_='css-1ap5wc6'):
            nuevas_monedas.add(item.text.strip())

        return nuevas_monedas

    except Exception as e:
        print(f"⚠️ Error al obtener monedas: {e}")
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

def cargar_usuarios():
    """Carga la lista de usuarios registrados."""
    try:
        with open(USERS_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_usuarios(usuarios):
    """Guarda la lista de usuarios registrados."""
    with open(USERS_FILE, "w") as file:
        json.dump(list(usuarios), file)

async def start(update: Update, context: CallbackContext):
    """Maneja el comando /start y registra el usuario."""
    chat_id = update.message.chat_id
    usuarios = cargar_usuarios()

    if chat_id not in usuarios:
        usuarios.add(chat_id)
        guardar_usuarios(usuarios)
        await update.message.reply_text("✅ Te has registrado para recibir alertas de nuevas monedas listadas en Binance.")
    else:
        await update.message.reply_text("🔔 Ya estás registrado. Recibirás notificaciones.")

async def iniciar_verificador():
    """Verifica nuevas monedas listadas en Binance cada 5 minutos."""
    while True:
        print("🔍 Verificando nuevas monedas en Binance...")
        monedas_actuales = obtener_monedas_binance()
        monedas_guardadas = cargar_monedas_guardadas()

        nuevas_monedas = monedas_actuales - monedas_guardadas

        if nuevas_monedas:
            usuarios = cargar_usuarios()
            for moneda in nuevas_monedas:
                mensaje = f"🚀 ¡Nueva moneda listada en Binance!\n🔹 **Token:** {moneda}"
                for user_id in usuarios:
                    try:
                        await app.bot.send_message(chat_id=user_id, text=mensaje)
                        print(f"📢 Notificación enviada a {user_id}: {moneda}")
                    except Exception as e:
                        print(f"⚠️ Error al enviar mensaje a {user_id}: {e}")

            guardar_monedas(monedas_actuales)
        else:
            print("✅ No hay nuevas monedas listadas.")

        await asyncio.sleep(300)  # Espera 5 minutos antes de volver a verificar

async def main():
    """Ejecuta el bot de Telegram y el verificador de monedas en paralelo."""
    global app
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Ejecutar el bot y el verificador en paralelo
    await asyncio.gather(
        app.run_polling(),
        iniciar_verificador()
    )

# 🔹 Ejecutar en un entorno estándar sin loops activos previamente
if __name__ == "__main__":
    asyncio.run(main())
