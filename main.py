import requests
from bs4 import BeautifulSoup
import json
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Configuración del bot de Telegram
TELEGRAM_TOKEN = "7463495309:AAFnWbMN8eYShhTt9UvygCD0TAFED-LuJhM"
bot = Bot(token=TELEGRAM_TOKEN)

# URL de Binance con nuevas criptomonedas listadas
BINANCE_NEW_COINS_URL = "https://www.binance.com/es/altcoins/new"

# Archivos donde guardamos datos
DATA_FILE = "listed_coins.json"
USERS_FILE = "usuarios.json"

def obtener_monedas_binance():
    """Obtiene la lista de nuevas monedas listadas en Binance."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; YourBot/1.0; +http://yourdomain.com/bot)"
        }
        response = requests.get(BINANCE_NEW_COINS_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

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

def cargar_usuarios():
    """Carga los usuarios registrados desde un archivo."""
    try:
        with open(USERS_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_usuarios(usuarios):
    """Guarda la lista de usuarios registrados."""
    with open(USERS_FILE, "w") as file:
        json.dump(list(usuarios), file)

async def notificar_nueva_moneda(moneda, usuarios):
    """Envía un mensaje a Telegram a todos los usuarios registrados."""
    mensaje = f"🚀 Nueva moneda listada en Binance: {moneda}"
    for chat_id in usuarios:
        try:
            asyncio.create_task(bot.send_message(chat_id=chat_id, text=mensaje))
            print(f"Mensaje enviado a {chat_id}: {mensaje}")
        except Exception as e:
            print(f"Error al enviar mensaje a {chat_id}: {e}")

async def verificar_nuevas_monedas():
    """Verifica si hay nuevas monedas listadas en Binance cada 5 minutos."""
    while True:
        print("🔍 Verificando nuevas monedas en Binance...")

        monedas_actuales = obtener_monedas_binance()
        monedas_guardadas = cargar_monedas_guardadas()
        nuevas_monedas = monedas_actuales - monedas_guardadas

        if nuevas_monedas:
            usuarios = cargar_usuarios()
            for moneda in nuevas_monedas:
                asyncio.create_task(notificar_nueva_moneda(moneda, usuarios))
            guardar_monedas(monedas_actuales)
        else:
            print("✅ No hay nuevas monedas listadas en Binance.")

        await asyncio.sleep(300)  # Espera 5 minutos antes de la siguiente verificación

async def start(update: Update, context: CallbackContext):
    """Registra al usuario y le da la bienvenida."""
    chat_id = update.effective_chat.id
    usuarios = cargar_usuarios()
    if chat_id not in usuarios:
        usuarios.add(chat_id)
        guardar_usuarios(usuarios)
        await update.message.reply_text("🚀 ¡Te has registrado con éxito! Recibirás notificaciones de nuevas monedas listadas en Binance.")
    else:
        await update.message.reply_text("✅ Ya estás registrado para recibir notificaciones.")

async def stop(update: Update, context: CallbackContext):
    """Elimina al usuario de la lista de notificaciones."""
    chat_id = update.effective_chat.id
    usuarios = cargar_usuarios()
    if chat_id in usuarios:
        usuarios.remove(chat_id)
        guardar_usuarios(usuarios)
        await update.message.reply_text("⛔ Has sido eliminado de las notificaciones.")
    else:
        await update.message.reply_text("❌ No estabas registrado para recibir notificaciones.")

async def main():
    """Inicia el bot de Telegram y la verificación de monedas en paralelo."""
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    print("🚀 Bot en ejecución...")
    
    async with app:
        # Ejecutar el bot y la verificación de monedas en paralelo
        task_bot = asyncio.create_task(app.run_polling())
        task_monedas = asyncio.create_task(verificar_nuevas_monedas())

        await asyncio.gather(task_bot, task_monedas)

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        print("⚠️ El bucle de eventos ya está en ejecución. Ejecutando el bot en segundo plano...")
        loop.create_task(main())
    else:
        print("✅ Iniciando un nuevo bucle de eventos.")
        asyncio.run(main())
