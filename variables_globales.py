from pyrogram import Client
from os import getenv
from mediafire.client import MediaFireClient
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime

API_HASH = "28aad172a316207be641435b1101d20a"
API_ID = 19096404
BOT_TOKEN = getenv("BOT_TOKEN")
NAME_APP = getenv("NAME_APP")
BOT_USER = getenv("BOT_USER")
PORT = getenv("PORT")
SESSION_STRING = getenv("SESSION_STRING")

try:
    from Debug import BOT_TOKEN, PORT, SESSION_STRING, BOT_USER

    print("MODO DEBUG")
    DEBUG = True
except:
    print("MODO ONLINE")
    DEBUG = False

app = Client(name="filemaster", api_hash=API_HASH, api_id=API_ID, bot_token=BOT_TOKEN)

userbot = Client(
    "userbot", API_ID, API_HASH, bot_token=BOT_TOKEN, session_string=SESSION_STRING
)

# CREDENCIALES DE GOOGLE DRIVE
gauth = GoogleAuth(settings_file="./conf.yaml")
gauth.LoadCredentialsFile("credentials_module.json")

if gauth.access_token_expired:
    gauth.Refresh()
    gauth.SaveCredentialsFile("credentials_module.json")
else:
    gauth.Authorize()

try:
    client = MediaFireClient()
    client.login(
        email="baitycasper@gmail.com", password="Spar1Syco7Shri0%", app_id="42511"
    )
except:
    pass

drive = GoogleDrive(gauth)

# =====================Variables Globales
saved_messages = {}
LISTA_ARCHIVOS = []
USER_ROOT = {}
CHOSE_FORMAT = {}
FECHA_INICIAL = datetime.now()
USERS = []
download_queues = {}
download_queues_url = {}
OPTIONS = {
    "save_description": "saveoff",
    "format_file": "zip",
    "format_video": "video",
    "auto_up": "desactivate",
    "zip_size": 2000,
}
# =====================Variables Globales
