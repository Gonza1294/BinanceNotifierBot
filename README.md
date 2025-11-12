# Crypto Telegram Socket Bot

Bot de Telegram para recibir notificaciones de trading y consultar balances en Binance.

## 🧩 Descripción
El bot escucha mensajes a través de un socket TCP y los envía a los usuarios autorizados en Telegram.  
También permite consultar saldos en Binance mediante el comando `/balance`.

## ⚙️ Estructura
- `telegram_bot.py` → Control principal del bot.
- `checkBinance.py` → Funciones de Binance API.
- `readConfig.py` → Lector de configuración desde YAML.
- `stylesMessages.json` → Plantillas de mensajes HTML.
- `user_ids.json` → Lista de usuarios con acceso (whitelist).
- `keys.json` → Claves privadas.
- `conf.yaml` → Configuración de rutas, IP y puertos.

## 🧾 Comandos disponibles
- `/start` → Registra al usuario.
- `/balance <coin>` → Devuelve saldo de la moneda especificada.
- `/checkPort` → Prueba de conexión con el socket.
- `/help` → Ayuda básica.

## 🧰 Requisitos
Python 3.9+  
Dependencias:
```bash
pip install -r requirements.txt
```

## 🧠 Configuración
1. Crea un archivo `keys.json` con tus credenciales:
   ```json
   {
     "api_key": "TU_API_KEY_BINANCE",
     "api_secret": "TU_API_SECRET_BINANCE",
     "telegram_token": "TU_TOKEN_TELEGRAM"
   }
   ```

2. Ajusta `conf.yaml` con tus rutas, puertos y paths:
   ```yaml
   path:
     keysFilePath: ./keys.json
     userIdPath: ./user_ids.json
     stylesMessagesPath: ./stylesMessages.json
     logTelegramPath: ./logs
   network:
     ip: 127.0.0.1
     port: 5555
   ```

3. Agrega a `user_ids.json` tus usuarios autorizados, al ejecutar el comando /start apareceran aqui con la opcion White List en False, para que funcione hay que modificar el fichero y asignarle True:
   ```json
   [
     { "user_id": 12345, "first_name": "Usuario", "username": "usuario", "whiteList": "true" }
   ]
   ```

## ▶️ Ejecución
```bash
python telegram_bot.py
```

## 🧱 Estructura del repositorio
```
crypto-telegram-socket-bot/
├── telegram_bot.py
├── checkBinance.py
├── readConfig.py
├── conf.yaml
├── keys.json
├── stylesMessages.json
├── user_ids.json
└── requirements.txt
```

## 📜 Licencia
MIT
