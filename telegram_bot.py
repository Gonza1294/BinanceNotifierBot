import json
import logging
import socket
import threading
import asyncio
import yaml 
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
import os
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, Application
from readConfig import readConfig
from checkBinance import getBalance


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(StreamHandler())
    logger.addHandler(RotatingFileHandler(os.path.join(readConfig(["path", "logTelegramPath"]), f"Telegram_bot.log"), maxBytes=1024 * 1024, backupCount=10))
    return logger

def registrar_usuario(message):
    try:
        with open(readConfig(["path", "userIdPath"]), 'r') as file:
            # Verificar si el archivo está vacío
            file_contents = file.read()
            if not file_contents:
                user_ids = []
            else:
                user_ids = json.loads(file_contents)
    except FileNotFoundError:
        user_ids = []

    user_id = message.from_user.id

    # Verificar si el user_id ya está en la lista
    if not any(user_data['user_id'] == user_id for user_data in user_ids):
        # Obtener información del usuario
        user_data = {
            'user_id': user_id,
            'first_name': message.from_user.first_name,
            'username': message.from_user.username,
            'whiteList': "false"
        }
        user_ids.append(user_data)
        with open(readConfig(["path", "userIdPath"]), 'w') as file:
            json.dump(user_ids, file, indent=4)
        print(f"Usuario ID {user_id} guardado correctamente.")
    else:
        print(f"El Usuario ID {user_id} ya está en el archivo.")

def readUsers():
    try:
        with open(readConfig(["path", "userIdPath"]), 'r') as file:
            user_ids = json.load(file)
            # Filtrar usuarios con whitelist en True
            whitelisted_users = [user_data['user_id'] for user_data in user_ids if user_data.get('whiteList') == "true"]
            return whitelisted_users
    except FileNotFoundError:
        return []
    
    
async def enviar_a_telegram(mensaje: str, token: str) -> None:
    # Enviar mensaje a través de Telegram.
    user_ids = readUsers()
    if user_ids:
        bot = Bot(token)
        for chat_id in user_ids:
            await bot.send_message(chat_id, text=mensaje, parse_mode='HTML')

async def recibir_mensaje_socket(server_socket, token):
    # Recibir mensajes a través del socket y enviarlos a Telegram.
    while True:
        client_socket, address = server_socket.accept()
        mensaje = client_socket.recv(1024).decode()
        output_log = {"mensaje":mensaje}
        logger.info(json.dumps(output_log))
        try:
            mensaje = json.loads(mensaje)
            mensaje_html = await setearMensaje(mensaje)
            await enviar_a_telegram(mensaje_html, token)
        except:
            await enviar_a_telegram(mensaje, token)

        client_socket.close()


async def setearMensaje(mensaje):
    try:
        # Cargar el archivo JSON de estilos de mensajes
        with open(readConfig(["path", "stylesMessagesPath"]), 'r') as file:
            style = json.load(file)

        # Obtener el formato de mensaje correspondiente a la acción del mensaje
        formato_mensaje = style["mensajes"].get(mensaje["action"], None)
        # Verificar si se encontró un formato de mensaje para la acción
        if formato_mensaje:
            # Unir las líneas de mensaje en una sola cadena
            mensaje_html = "\n".join(formato_mensaje)
            # Reemplazar las variables en el mensaje con los valores proporcionados en 'mensaje'
            mensaje_html = mensaje_html.format(**mensaje)
            return mensaje_html
        else:
            return f"Acción {mensaje['action']} no reconocida"
    except Exception as e:
        # Manejar cualquier excepción y devolver un mensaje de error
        return f"Error al cargar los estilos de mensajes: {e}, Mensaje: {mensaje}"


async def getBalanceBinance(update, context):
    try:
        if not context.args:  # Verifica si el parámetro 'coin' está presente
            await enviar_a_telegram("Se requiere un parámetro 'coin' para obtener el balance", context.bot.token)
        else:
            balance = getBalance(update, context, context.args[0])
            mensaje = f"El balance es: {balance} {context.args[0].upper()}"
            await enviar_a_telegram(mensaje, context.bot.token)
    except ValueError as e:
        await enviar_a_telegram(str(e), context.bot.token)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Primer mensaje que se recibe al entrar al bot o poner /start
    user = update.effective_user
    registrar_usuario(update.message)
    await update.message.reply_html(
        rf"Hola {user.mention_html()}, pide permiso para poder utilizar el bot si no lo tienes ya.",
    )


def enviar_mensaje_socket(update, context):
    """Enviar mensaje a través del socket."""
    server_host = readConfig(["network", "ip"])
    server_port = readConfig(["network", "port"])
    try:
        if not context.args:  # Verifica si el parámetro 'coin' está presente
            mensaje = "Prueba de funcionamiento de Shocket"
        else:
            mensaje = f"Mensaje de prueba: {str(context.args[0])}"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((server_host, server_port))
                print("Conectado!")
                client_socket.sendall(mensaje.encode())
                print("Mensaje Enviado!")

            except Exception as e:
                print(f"No se pudo conectar al servidor: {e}")
                return
            
    except ValueError as e:
        print(str(e), context.bot.token)



async def help_command(update, context):
    await update.message.reply_text("¡Ayuda!")


def main():
    # Configurar el registro
    #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Leer la configuración desde el archivo JSON
    with open(readConfig(["path", "keysFilePath"]), 'r') as file:
        config = json.load(file)
        bot_token = config['telegram_token']
        
    app = ApplicationBuilder().token(bot_token).build()

    server_host = readConfig(["network", "ip"])
    server_port = readConfig(["network", "port"])
    

    # Configurar el socket del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((str(server_host), server_port))
        server_socket.listen(5)
        print("Socket del servidor configurado y en escucha correctamente.")
    except Exception as e:
        print(f"No se pudo configurar el socket del servidor: {e}")

    # Iniciar el hilo para recibir mensajes del socket y enviarlos a Telegram
    recibir_thread = threading.Thread(target=lambda: asyncio.run(recibir_mensaje_socket(server_socket, bot_token)))
    recibir_thread.start()

    # Registrar los controladores
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", getBalanceBinance))
    app.add_handler(CommandHandler("checkPort", enviar_mensaje_socket))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    logger = setup_logging()
    main()
