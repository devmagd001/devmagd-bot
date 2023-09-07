import pytz
from shutil import rmtree, move
from UploadFiles import uploadFiles, uploadOnefile, compressfiles, compressSelectedFiles
from progrs import progressddl
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from unicodedata import normalize
from psutil import virtual_memory, disk_usage
from queue import Queue as cola
from pyrogram.errors import ChannelBanned, ChannelInvalid,ChannelPrivate, ChatIdInvalid, ChatInvalid
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid,InviteHashExpired,UserAlreadyParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply, InputMediaPhoto, InputMediaDocument, InputMediaVideo
from ModulesDownloads.compress import split, getBytes
from tools import cleanString, download_youtube, extractInfoVideo, mostrar_opciones, showFiles, DIC_FILES, extractImg, sendInfo
from asyncio import sleep as asyncsleep, Queue
from aiohttp import ClientSession
from aiohttp import web
from server import download_file, submit_handler, index, usr_path
from time import time as tm, gmtime, sleep
from datetime import datetime
from random import randint
from pyrogram.methods.utilities.idle import idle
from Downloads import DownloadFiles
from os import listdir, mkdir, getenv, unlink, rename
from os.path import getsize, join, isdir, isfile, exists
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from zipfile import ZipFile
from rarfile import RarFile
from py7zr import SevenZipFile
from pickle import dumps, loads
from requests import post, delete, get
from cv2 import resize, imread, imwrite
from json import dumps
from ModulesDownloads.file_tipeClass import fileType
from progrs import text_progres
from subprocess import run, PIPE

# CREDENCIALES DE GOOGLE DRIVE
gauth = GoogleAuth(settings_file='./conf.yaml')
gauth.LoadCredentialsFile("credentials_module.json")

if gauth.access_token_expired:
    gauth.Refresh()
    gauth.SaveCredentialsFile("credentials_module.json")
else:
    gauth.Authorize()

drive = GoogleDrive(gauth)
API_HASH = "28aad172a316207be641435b1101d20a"
API_ID = 19096404
BOT_TOKEN = getenv("BOT_TOKEN")
NAME_APP = getenv("NAME_APP")
BOTUSER = getenv('BOTUSER')
PORT = getenv('PORT')
SESSION_STRING = getenv('SESSION_STRING')

try:
    from Debug import BOT_TOKEN, PORT, SESSION_STRING
    print("MODO DEBUG")
    DEBUG = True
except:
    print("MODO ONLINE")
    DEBUG = False

app = Client(name="filemaster", api_hash=API_HASH,
             api_id=API_ID, bot_token=BOT_TOKEN)
userbot = Client("userbot", API_ID, API_HASH, bot_token=BOT_TOKEN, session_string=SESSION_STRING)

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
    'save_description' : 'saveoff',
    'format_file'      : 'zip',
    'format_video'     : 'video', 
    'auto_up'          : 'desactivate',
    'zip_size'         :  2000,
}

# =====================Variables Globales

@app.on_message(filters.text & filters.forwarded & filters.private)
def send_Infos(app, message):
    if message.from_user.username == 'KOD_16':
        sendInfo(message)

@app.on_inline_query()
def handle_inline_query(client, query):
    global DIC_FILES
    FOLDER_FILES = listdir(query.from_user.username)
    count = 0
    listfiles = f"**📂 RUTA: `./{query.from_user.username}`**\n\n"
    fileSize = 0
    DIC_ARCH = {}
    for i in FOLDER_FILES:
        count += 1
        fileSize = round(getsize(join(query.from_user.username, i)) / 1000024, 2)
        DIC_ARCH[count] = i
        if i.endswith('zip') or i.endswith('rar') or i.endswith('7z'):
            listfiles += f"📦 **{fileSize} MB - `{i}`**\n\n"
        elif i[-3] == '0':
            listfiles += f"🧩 **{fileSize} MB - `{i}`**\n\n"
        elif isdir(f'{query.from_user.username}/{i}'):
            listfiles += f"📁 `{i}`\n\n"
        else:
            listfiles += f"● **{fileSize} MB - `{i}`**\n\n"
        
    listfiles += f"**⚖️ TAMAÑO TOTAL: {round(fileSize, 2)} MB\n**"
    DIC_FILES[query.from_user.username] = DIC_ARCH
        
    TXT = "**__MEMORIA RAM__**\n"
    TXT += f"**● TOTAL: `{round(virtual_memory().total / 1024 ** 2)} MB`**\n"
    TXT += f"**● DISPONIBLE: `{round(virtual_memory().available / 1024 ** 2)} MB`**\n"
    TXT += f"**● USADA: `{round(virtual_memory().used / 1024 ** 2)} MB`**"
    TXT += f"**{text_progres(round(virtual_memory().used / 1024 ** 2), round(virtual_memory().total / 1024 ** 2))}**"
    TXT += "**\n\n__ALMACENAMIENTO__**\n"
    TXT += f"**● TOTAL: `{round(disk_usage('/').total / (1024**2))} MB`**\n"
    TXT += f"**● LIBRE: `{round(disk_usage('/').free / (1024**2))} MB`**\n"
    TXT += f"**● OCUPADO: `{round(disk_usage('/').used / (1024**2))} MB`**"
    TXT += f"**{text_progres(round(disk_usage('/').used / (1024**3)), round(disk_usage('/').total / (1024**3)))}**"
    TXT += f"**\n\n⏱ __Tiempo activo: {str(datetime.now() - FECHA_INICIAL).split('.')[0]}__**"
        
    query.answer(
        results=[
            InlineQueryResultArticle(
                title="Archivos",
                input_message_content=InputTextMessageContent(listfiles),
                description="Mostrar los archivos en el Bot"),
            InlineQueryResultArticle(
                title="Estado",
                input_message_content=InputTextMessageContent(message_text=TXT),
                description="Mostrar estado del Bot")
            ] 
    )
    
# ============================================================================================================== #
# =========================================== CALLBACK QUERY =================================================== #
# ============================================================================================================== #

@app.on_callback_query(filters.create(lambda f, c, u: u.data == 'up_all'))
async def subir_todo(app, callback_query):
    global saved_messages
    SMS = callback_query.message
    username = callback_query.from_user.username

    try:
        for i in saved_messages[username]["sms_files"]:
            await i.delete()
    except:
        pass
    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"
    stk = await SMS.reply_sticker("./assets/subiendo.tgs")
    FOLDER_FILES = listdir(directory)
    FOLDER_FILES.sort()
    count = 0
    for i in FOLDER_FILES:
        if isfile(join(directory, i)):
            count += 1
            await uploadOnefile(app, SMS, i, directory, len(FOLDER_FILES), count)
    await SMS.reply_sticker("./assets/fin.webp")
    await stk.delete()

@app.on_callback_query(filters.create(lambda f, c, u: u.data == 'borrartodo'))
def borrar_todo(app, callback_query):
    global saved_messages
    username = callback_query.from_user.username
    if "CallbackQuery" in str(callback_query).split(':')[1]: SMS = callback_query.message
    else: SMS = callback_query
        
    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"
    try:
        for i in saved_messages[username]["sms_files"]:
            i.delete()
    except: pass
    
    for i in listdir(directory):
        if isfile(join(directory, i)):
            unlink(join(directory, i))
            
    saved_messages = showFiles(
        app, SMS, saved_messages, directory, username)

@app.on_callback_query()
def callbackQuery(app, callback_query):
    global DIC_FILES
    global saved_messages
    global USER_ROOT
    global OPTIONS

    username = callback_query.from_user.username
    SMS = callback_query.message
    CALLBACK_DATA = callback_query.data
    BUTTON_BACK = InlineKeyboardMarkup(
        [[InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
    WORKING[username] = False

    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"

    # **************************************** VER ARCHIVOS ****************************************

    if CALLBACK_DATA == 'ver':
        SMS.delete()
        saved_messages = showFiles(
            app, SMS,  saved_messages, directory, username)

        # **************************************** RETROCEDER DIRECTORIO *********************************************

    elif CALLBACK_DATA == 'back':
        USER_ROOT[username] = "/".join(USER_ROOT[username].split('/')[:-1])
        try: directory = USER_ROOT[username]
        except: directory = username
        try:
            for i in saved_messages[username]["sms_files"]: i.delete()
        except: pass
        saved_messages = showFiles(
            app, SMS,   saved_messages, directory, username)

        # **************************************** ATRAS *********************************************

    elif CALLBACK_DATA == 'backk':
        SMS.delete()
        try:
            for i in saved_messages[username]["sms_files"]: i.delete()
        except: pass
        saved_messages = showFiles( app, SMS, saved_messages, directory, username)

        # **************************************** OPCIONES *********************************************

    elif CALLBACK_DATA == 'option':
        try:
            for i in saved_messages[username]["sms_files"]: i.delete()
        except: pass
        mostrar_opciones(SMS)

        # **************************************** SUBIR ARCHIVO *********************************************

    elif CALLBACK_DATA == 'savedesc':
        MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('✅ ACTIVAR', callback_data='saveon'),
                                       InlineKeyboardButton('☑️ DESACTIVAR', callback_data='saveoff')],
                                       [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
        SMS.edit_text('**Seleccione una opcion**', reply_markup=MARKUP)

    elif CALLBACK_DATA == 'saveon':
        OPTIONS['save_description'] = 'saveon'
        SMS.edit_text("**Los archivos de Telegram se descargarán con el nombre que tenga en su descripción.**",
                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))

    elif CALLBACK_DATA == 'saveoff':
        OPTIONS['save_description'] = 'saveoff'
        SMS.edit_text("**☑️ DESACTIVADO**", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))

        # **************************************** COMPRIMIR ARCHIVOS ****************************************

    elif CALLBACK_DATA == 'compres':
        SMS.delete()
        SMS.reply("**📝 Introduzca el nombre para el zip\n🔑 Debajo una contraseña (Opcional)**",
                  reply_markup=ForceReply())

        # **************************************** SUBIR ARCHIVOS ****************************************

    elif CALLBACK_DATA == 'upload':
        SMS.delete()
        SMS.reply("**📝 Introduzca el nombre del zip\n🔑 Debajo una contraseña (Opcional)**",
                  reply_markup=ForceReply())

    # **************************************** BORRAR SMS ****************************************

    elif CALLBACK_DATA == 'borrarsms':
        callback_query.message.delete()

    # **************************************** ELEGIR FORMATO DE ZIPS ****************************************

    elif CALLBACK_DATA == "formatfile":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('ZIP', callback_data='zip'), InlineKeyboardButton('7z', callback_data='7z')],
                                       [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
        SMS.edit_text('**📚 Elige el formato de compresión **', reply_markup=markup)

    elif CALLBACK_DATA == "zip" or CALLBACK_DATA == "7z":
        
        SMS.edit_text(f"**✅ Done, the format will be: `{CALLBACK_DATA}`**", reply_markup=BUTTON_BACK)

    # **************************************** SUBIDA AUTOMATICA ****************************************#

    elif CALLBACK_DATA == "autoup":
        MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('📦 COMPRIMIDOS', callback_data='up_compress'),
                                        InlineKeyboardButton('📄 SIN COMPRIMIR', callback_data='up_noCompress')],
                                       [InlineKeyboardButton(
                                           '☑️ DESACTIVAR', callback_data='desactivate')],
                                       [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
        SMS.edit_text(
            "**Cómo desea subir los archivos de forma automática?**", reply_markup=MARKUP)

    elif CALLBACK_DATA == "up_compress":
        OPTIONS['auto_up'] = 'up_compress'
        SMS.edit_text("📦 **Los archivos se subirán comprimidos**",
                      reply_markup=BUTTON_BACK)

    elif CALLBACK_DATA == "up_noCompress":
        OPTIONS['auto_up'] = 'up_noCompress'
        SMS.edit_text("📄 **Los archivos se subirán sin comprimir**",
                      reply_markup=BUTTON_BACK)

    elif CALLBACK_DATA == "desactivate":
        OPTIONS['auto_up'] = 'desactivate'
        SMS.edit_text(" **Subida automática ☑️ DESACTIVADA**",
                      reply_markup=BUTTON_BACK)

    # **************************************** AÑADIR THUMB ****************************************#

    elif CALLBACK_DATA == "tumb":
        SMS.delete()
        SMS.reply('🌠 **Envíame una imagen para mostrar en el archivo cuando se suba a Telegram**',
                  reply_markup=ForceReply())

    # **************************************** ELEGIR TAMAÑO DE ZIPS ****************************************#

    elif CALLBACK_DATA == 'zipsize':
        SMS.delete()
        SMS.reply('**📚 Introduzca el tamaño de los zips: **',
                  reply_markup=ForceReply())

    # **************************************** DESCARGAR VIDEO ****************************************#

    elif CALLBACK_DATA.startswith("dlvid"):
        WORKING[username] = True
        message = callback_query.message
        message.delete()

        IDFORMAT = CALLBACK_DATA.split("-")[1]
        format = CHOSE_FORMAT[username][int(IDFORMAT)][:-1]
        
        if callback_query.message.reply_to_message.text.startswith('/video'):
            url = callback_query.message.reply_to_message.text.split(' ')[-1]
        else:
            url = callback_query.message.reply_to_message.text
            
        file_info = (message, url, username, directory, format)
    
        if username in download_queues_url: download_queues_url[username].put(file_info)
        else:
            queue = cola()
            queue.put(file_info)
            download_queues_url[username] = queue
            descargar_archivos_url(username)

    # **************************************** ELEGIR FORMATO DE VIDEO **************************************** #

    elif CALLBACK_DATA == 'formatvideo':
        SMS.edit_text("**Eliga cómo se subirán los vídeos a Telegram:**", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎞 VIDEO", callback_data="Video"), InlineKeyboardButton(
                "📄 DOCUMENTO", callback_data="Documento")],
            [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]]))
        
    elif CALLBACK_DATA == 'Video':
        OPTIONS['format_video'] = 'video'
        SMS.edit_text("**🎞 VIDEO**", reply_markup=BUTTON_BACK)
        
    elif CALLBACK_DATA == 'Documento':
        OPTIONS['format_video'] = 'documento'
        SMS.edit_text("**📄 DOCUMENTO**", reply_markup=BUTTON_BACK)

# ******************************************************************************************************** #
# ******************************************* RESPONDER MENSAJES ***************************************** #
# ******************************************************************************************************** #

@app.on_message(filters.command('add_buttons') & filters.reply)
def Agregar_botones(app, message):
    global saved_messages
    global OPTIONS
    
    Txt = '**Para crear botones, necesitas proporcionar el nombre del botón y la URL del enlace que deseas que el botón lleve. El formato es el siguiente:\n'
    Txt += '\n`Nombre del Botón - URL` (Funciona con http y @)**'
    message.reply(Txt, reply_to_message_id=message.reply_to_message.id,
                  reply_markup=ForceReply())
    saved_messages[message.from_user.username] = {
        'SMS_BOTONES': message.reply_to_message}

@app.on_message(filters.command('carbon'))
def CarbonAPI(app, message):
    URL = 'https://carbonara.solopov.dev/api/cook'
    CODE = message.text.replace('/carbon\n', '').replace(
        '/carbon@rey_testingBot\n', '').replace('/carbon@File_MasterBot\n', '')
    print("Obteniendo Informacion", CODE)
    JSON = {
        'code': f'{CODE}',
        'backgroundColor': '#FFFFFF00',
        'theme': 'monokai',
        'language': 'python'
    }

    IMG = post(URL, json=JSON)
    with open(f'{message.from_user.username}/Carbon.png', 'wb') as f:
        f.write(IMG.content)
    message.reply_photo(f'{message.from_user.username}/Carbon.png')
    unlink(f'{message.from_user.username}/Carbon.png')


@app.on_message(filters.reply & filters.create(lambda f, c, u: u.reply_to_message.text.startswith('📝 Introduzca el nombre del zip')))
async def subirArchivosComprimidos(app, message):
    try:
        directory = USER_ROOT[message.from_user.username]
    except:
        directory = f"{message.from_user.username}"
    await message.reply_to_message.delete()
    await message.delete()
    FOLDER_FILES = listdir(directory)
    await uploadFiles(app, message, message.text, directory, FOLDER_FILES)

@app.on_message(filters.reply)
def Responder_Mensajes(app, message):
    SMS_REPLY = message.reply_to_message
    global USER_ROOT
    global WORKING

    try:
        if SMS_REPLY.text.startswith('@'):
            user = app.get_users(SMS_REPLY.text[1:])
            app.send_message(user.id, message.text)
    except:
        pass
    username = message.from_user.username
    BUTTON_BACK = InlineKeyboardMarkup(
        [[InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='ver')]])
    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"

      # =============================== AÑADIR THUMB ===============================#

    if SMS_REPLY.text == '🌠 Envíame una imagen para mostrar en el archivo cuando se suba a Telegram':
        SMS_REPLY.delete()

        try:
            saved_messages[username]['sms_thumb'].delete()
        except:
            pass

        ID = message.reply('**⏳ PROCESANDO...**')
        try:
            FILE = message.download(file_name='./')
            IMG = imread(FILE)
            Alto, Ancho = IMG.shape[:2]
            if Ancho > Alto:
                Alto = int(Alto * 320 / Ancho)
                Ancho = 320
            else:
                Ancho = int(Ancho * 320 / Alto)
                Alto = 320

            IMG = resize(IMG, (Ancho, Alto))
            imwrite(f"{username}-thumb.jpg", IMG)
            unlink(FILE)
            id_doc = message.reply_document(
                f"{username}-thumb.jpg", reply_markup=BUTTON_BACK)
            message.delete()
            ID.delete()

        except Exception as x:
            return message.reply(f"🚫 **Ah ocurrido un error\n{x}** 🚫", reply_markup=BUTTON_BACK)
        return

       # =============================== ENVIAR BOTONERA ===============================#

    if SMS_REPLY.text.startswith('Para crear botones, necesitas proporcionar el nombre del botón y la URL del enlace que deseas que el botón lleve. El formato es el siguiente:'):
        filas = message.text.split("\n\n")
        SMS_REPLY.delete()
        try:
            if len(filas) == 1:
                column = filas[0].split("\n")
                btn = []
                for i in column:
                    btn.append(InlineKeyboardButton(
                        i.split(" - ")[0], url=i.split(" - ")[1].replace("@", "https://t.me/")))
                botones = InlineKeyboardMarkup([btn])
            else:
                column = []
                for f in filas:
                    btn = []
                    for i in f.split("\n"):
                        btn.append(InlineKeyboardButton(
                            i.split(" - ")[0], url=i.split(" - ")[1].replace("@", "https://t.me/")))
                    column.append(btn)
                    botones = InlineKeyboardMarkup(column)
        except Exception as x:
            message.reply(f'🚫 DATOS INCORRECTOS\n\n{x}')
        try:
            if username in saved_messages and 'SMS_BOTONES' in saved_messages[username]:
                saved_messages[username]['SMS_BOTONES'].copy(
                    message.chat.id, reply_markup=botones)
                saved_messages[username].pop('SMS_BOTONES')
                SMS_REPLY.delete()
            else:
                global LISTA_ARCHIVOS
                for i in LISTA_ARCHIVOS:
                    sleep(0.50)
                    if username in i.keys():
                        MSG = i[username][0]
                        MSG.copy(message.chat.id, reply_markup=botones)
                        i[username][1].delete()
                        LISTA_ARCHIVOS.remove(i)
                sleep(0.50)
                for i in LISTA_ARCHIVOS:
                    if username in i.keys():
                        MSG = i[username][0]
                        MSG.copy(message.chat.id, reply_markup=botones)
                        i[username][1].delete()
                        LISTA_ARCHIVOS.remove(i)
                sleep(0.50)
                for i in LISTA_ARCHIVOS:
                    if username in i.keys():
                        MSG = i[username][0]
                        MSG.copy(message.chat.id, reply_markup=botones)
                        i[username][1].delete()
                        LISTA_ARCHIVOS.remove(i)
        except Exception as x:
            message.reply(x)

        # =============================== RENOMBRAR ARCHIVOS ===============================#

    elif SMS_REPLY.text.startswith("📝 Escriba un nuevo nombre para: "):
        oldname = SMS_REPLY.text.split(': ')[1]
        ext = oldname[5:].split('.')[-1]
        if isdir(join(directory, oldname)):
            FOLDER = message.text
            FOLDER = normalize('NFKD', FOLDER).encode(
                'ascii', 'ignore').decode('utf-8', 'ignore')
            FOLDER = ''.join(c for c in FOLDER if ord(c) < 128)
            FOLDER = FOLDER.replace(" ", "_")
            rename(f'{directory}/{oldname}', f'{directory}/{FOLDER}')
            message.reply(
                f'**☑️ Nombre Antiguo: ~~{oldname}~~\n✅ Nombre Nuevo: --{FOLDER}--**', reply_markup=BUTTON_BACK)
        else:
            rename(f'{directory}/{oldname}', f'{directory}/{message.text}')
            message.reply(
                f'**☑️ Nombre Antiguo: ~~{oldname}~~\n✅ Nombre Nuevo: --{message.text}--**', reply_markup=BUTTON_BACK)

        message.delete()
        SMS_REPLY.delete()

        # =============================== COMPRIMIR ARCHIVOS ===============================#

    elif SMS_REPLY.text == '📝 Introduzca el nombre para el zip\n🔑 Debajo una contraseña (Opcional)':
        SMS_REPLY.delete()
        message.delete()
        compressfiles(app, message, message.text, directory)
        message.reply("**✅ COMPRESION FINALIZADA**", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))

        # =============================== ZIPS SIZE ===============================#

    elif SMS_REPLY.text == '📚 Introduzca el tamaño de los zips:':
        try:
            zips = int(message.text)
            if zips >= 1 and zips <= 2000:
                OPTIONS['zip_size'] = zips
                message.reply(f"✅ **Zips establecidos en: [ `{zips} MB` ]**", reply_markup=BUTTON_BACK)
            else:
                message.reply('❌ **Debes introducir un número entre 1 y 2000**', reply_markup=BUTTON_BACK)
        except ValueError:
            message.reply('❌ **Debes introducir solo números**',
                          reply_markup=BUTTON_BACK)

        # =============================== COMPRIMIR ARCHIVOS ESCOGIDOS ===============================#

    elif SMS_REPLY.text.startswith("📂 Archivos para comprimir: "):
        WORKING[username] = True
        SMS_REPLY.delete()
        message.delete()
        compressSelectedFiles(message, message.text, username,
                              saved_messages[username]["listCompress"],  directory)
        message.reply("**✅ Compresión realizada**", reply_markup=BUTTON_BACK)
        WORKING[username] = False

# ******************************************************************************************************** #
# ******************************************* RECIBIR MENSAJES ******************************************* #
# ******************************************************************************************************** #

@app.on_message(filters.regex('/up_') & ~ filters.regex('/up_all') & ~ filters.regex('/up_album'))
async def subirArchivo(app, message):
    global saved_messages
    try:
        for i in saved_messages[message.from_user.username]["sms_files"]: await i.delete()
    except: pass
    FILE_NAME = DIC_FILES[message.from_user.username].get(int(message.text.replace('/up_', '')))
    try: directory = USER_ROOT[message.from_user.username]
    except: directory = f"{message.from_user.username}"
    await uploadOnefile(app, message, FILE_NAME, directory,  1, 1)

@app.on_message(filters.command('status'))
async def estadoBot(app, message):
    TXT = "**__MEMORIA RAM__**\n"
    TXT += f"**● TOTAL: `{round(virtual_memory().total / 1024 ** 2)} MB`**\n"
    TXT += f"**● DISPONIBLE: `{round(virtual_memory().available / 1024 ** 2)} MB`**\n"
    TXT += f"**● USADA: `{round(virtual_memory().used / 1024 ** 2)} MB`**"
    TXT += f"**{text_progres(round(virtual_memory().used / 1024 ** 2), round(virtual_memory().total / 1024 ** 2))}**"
    TXT += "**\n\n__ALMACENAMIENTO__**\n"
    TXT += f"**● TOTAL: `{round(disk_usage('/').total / (1024**2))} MB`**\n"
    TXT += f"**● LIBRE: `{round(disk_usage('/').free / (1024**2))} MB`**\n"
    TXT += f"**● OCUPADO: `{round(disk_usage('/').used / (1024**2))} MB`**"
    TXT += f"**{text_progres(round(disk_usage('/').used / (1024**3)), round(disk_usage('/').total / (1024**3)))}**"
    TXT += f"**\n\n⏱ __Tiempo activo: {str(datetime.now() - FECHA_INICIAL).split('.')[0]}__**"
    await message.reply(TXT)

@app.on_message(filters.command('up_album'))
async def subirAlbum(app, message):
    try: directory = USER_ROOT[message.from_user.username]
    except: directory = f"{message.from_user.username}"
    try:
        for i in saved_messages[message.from_user.username]["sms_files"]: await i.delete()
    except: pass
    stk = await message.reply_sticker("./assets/subiendo.tgs")
    FOLDER_FILES = listdir(directory)
    FOLDER_FILES.sort()
    ListPhotos = []
    ListVideo = []
    ListDocument = []
    if exists(f"./{message.from_user.username}-thumb.jpg"): thumb = f"./{message.from_user.username}-thumb.jpg"
    else: thumb = "./assets/thumb.jpg"
    for i in FOLDER_FILES:
        if fileType(i).isPhoto():
            if getsize(join(directory, i))/1048576 > 9:
                ListDocument.append(InputMediaDocument(join(directory, i)))
                if len(ListDocument) == 10:
                    await app.send_media_group(message.chat.id, ListDocument)
                    ListDocument = []
            else:
                ListPhotos.append(InputMediaPhoto(join(directory, i)))
                if len(ListPhotos) == 10:
                    await app.send_media_group(message.chat.id, ListPhotos)
                    ListPhotos = []

        elif fileType(i).isVideo():
            thumb, seconds = extractInfoVideo(
                join(directory, i), message.from_user.username)

            ListVideo.append(InputMediaVideo(
                join(directory, i), thumb=thumb, duration=seconds, supports_streaming=True))
            if len(ListVideo) == 10:
                await app.send_media_group(message.chat.id, ListVideo)
                ListVideo = []

        else:
            ListDocument.append(InputMediaDocument(
                join(directory, i), thumb=thumb))
            if len(ListDocument) == 10:
                await app.send_media_group(message.chat.id, ListDocument)
                ListDocument = []

    await app.send_media_group(message.chat.id, ListPhotos)
    await app.send_media_group(message.chat.id, ListVideo)
    await app.send_media_group(message.chat.id, ListDocument)
    await stk.delete()

@app.on_message(filters.command('extractimg'))
async def extraer_imagenes(app, message):
    try:
        num = message.text.split(" ")[1]
        if num.isdigit():
            file = DIC_FILES[message.from_user.username].get(int(num))
            if file.endswith(".mp4") or file.endswith(".mkv"):
                sms = await message.reply(
                    f"🖨** Extrayendo Imagenes de: \n`{file}`**")
                LsImg = extractImg(file, message.from_user.username)
                exportimg = []
                print("Enviando Imagenes")
                for i in LsImg:
                    exportimg.append(InputMediaPhoto(i))
                await message.reply_media_group(exportimg)
                await sms.edit_text(f"**🌄 Imágenes extraídas de: \n`{file}`**")
                rmtree(message.from_user.username + "/IMG")
            else: await message.reply("⚠️ El archivo seleccionado no es un video válido")
        else: await message.reply("**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/extractimg 1`**")
    except Exception as x:
        print(x)
        rmtree(message.from_user.username + "/IMG")
        await message.reply("**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/extractimg 1`**")
        
@app.on_message(filters.command('c') & filters.user("KOD_16"))
def comandos(app, message):
    param = message.text.split()
    if len(param) == 1: 
        message.reply("**No has indicado ningun comando**")
    else:
        comando = " ".join(param[1:])
        r = run(comando, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        texto = ""
        if r.returncode:
            texto+= f'**ERROR {r.returncode}**\n'
        else:
            if not r.stdout and not r.stderr: texto += "**Comando ejecutado correctamente**\n"
        if r.stdout: texto+=r.stdout
        if r.stderr: texto+=r.stderr
        message.reply(texto)

@app.on_message(filters.command('print') & filters.user("KOD_16"))
def show_variables(app, message):
    message.reply(f'**{globals()[message.text.split(" ")[-1]]}**')

# ===============================************************=============================== #
# ===============================* DESCARGAR DE ENLACES *=============================== #
# ===============================************************=============================== #

@app.on_message(filters.text & filters.create(lambda f, c, u: u.text.startswith('http')))
def descargar_enlaces(app, message):
    global CHOSE_FORMAT
    global saved_messages
    keywords = ['youtu.be', 'twitch', 'fb.watch', 'www.xvideos.com', 'www.xnxx.com', 'www.yourupload.com']
    username = message.from_user.username
    try:directory = USER_ROOT[message.from_user.username]
    except:directory = message.from_user.username
    
    try:
        for i in saved_messages[username]["sms_files"]:i.delete()
    except:pass
    
    if any(keyword in message.text for keyword in keywords): 
        CHOSE_FORMAT, saved_messages = download_youtube(message, message.text, CHOSE_FORMAT, username, saved_messages)
        return

    file_info = (message, message.text, message.from_user.username, directory, None)
    message.reply('📌 __Enlace añadido a la cola__', quote=True)
    if username in download_queues_url: download_queues_url[username].put(file_info)
    else:
        queue = cola()
        queue.put(file_info)
        download_queues_url[username] = queue
        descargar_archivos_url(username)
        
def descargar_archivos_url(username):
    global saved_messages
    global download_queues
    queue = download_queues_url[username]
    try:mkdir(username)
    except:pass
    
    while not queue.empty():
        message, url, username, directory, format = queue.get()
        try: DownloadFiles(app, userbot, message, url, username,  directory, format, queue.qsize())
        except Exception as x:message.reply(x)
        queue.task_done()
        
    saved_messages = showFiles(app, message,   saved_messages, directory, username)
    del download_queues_url[username]

# ===============================************************=============================== #
# ===============================* RECIBIR MENSAJES     *=============================== #
# ===============================************************=============================== #

@app.on_message(filters.text & filters.private)
def Recibir_Mensajes(app, message):

    global LISTA_ARCHIVOS
    global saved_messages
    global LISTA_ARCHIVOS
    global USER_ROOT
    global CHOSE_FORMAT
    global WORKING
    # ID CHAT: -1001718820562

    username = message.from_user.username
    try:
        mkdir(username)
    except:
        pass
    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"
    BUTTON_BACK = InlineKeyboardMarkup(
        [[InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='ver')]])
    BUTTON_FILES = InlineKeyboardMarkup(
        [[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]])
    SMS_TEXT = message.text
    CHAT_ID = message.chat.id
    
    ################################ COMANDOS ################################

    if SMS_TEXT.startswith("/start"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        try:
            username = message.from_user.username
        except:
            message.reply(
                "**Debe tener un nombre de usuario para usar el Bot**")
        try:
            mkdir(username)  # CREAR CARPETA
        except:
            pass
        TXT = f"""**
Bienvenido [{message.from_user.first_name}](https://t.me/{username}), le agradezco por contratar mi servicio. 😊
Estoy aquí para ofrecerle un servicio de calidad y profesional. 
Espero que le guste mi servicio y que se sienta satisfecho. 😊
        **"""
        sms = message.reply(TXT,
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton('🚀 INICIAR 🚀', callback_data='ver')]]),
                            disable_web_page_preview=True)

    # =============================== OPCIONES ===============================#

    elif SMS_TEXT.startswith("/opciones"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        mostrar_opciones(message)
        
    elif SMS_TEXT.startswith('/clean_all'):
        borrar_todo(app, message)

        # =============================== CAMBIAR DE DIRECTORIO ===============================#

    if SMS_TEXT.startswith("/cd_"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        FOLDER = DIC_FILES[username].get(int(SMS_TEXT.replace('/cd_', '')))
        directory = f"{directory}/{FOLDER}"
        USER_ROOT[username] = directory
        saved_messages = showFiles(
            app, message,   saved_messages, directory, username)

        # =============================== MOVER ARCHIVOS A UNA CARPETA ===============================#

    elif SMS_TEXT.startswith("/mover"):
        try:
            NUM = SMS_TEXT.split(" ")[1]
            FOLDER = SMS_TEXT.split(" ")[-1]

            if '/' not in FOLDER:
                if isfile(join(directory, DIC_FILES[username].get(int(FOLDER)))):
                    raise ValueError(
                        'El numero indicado no corresponde a una carpeta')

            if '-' in NUM:
                INDEX = tuple(NUM.split('-'))
                if int(INDEX[0]) < int(INDEX[-1]):
                    TXT = "**╔📄 Moviendo archivos...**\n║\n"
                    MSG = message.reply(TXT)
                    for i in range(int(INDEX[0]), int(INDEX[-1]) + 1):
                        FILE = join(directory, DIC_FILES[username].get(i))
                        if isfile(FILE):
                            TXT += f"**╠📄 **__{DIC_FILES[username].get(i)}__\n"
                            MSG.edit_text(f"\n{TXT}")
                            sleep(0.50)
                            if '/' in FOLDER:
                                NAME_FOLDER = directory.split("/")[-2]
                                move(FILE, directory.split("/")[-2])
                            else:
                                NAME_FOLDER = DIC_FILES[username].get(
                                    int(FOLDER))
                                move(FILE, join(
                                    directory, DIC_FILES[username].get(int(FOLDER))))

                    MSG.edit_text(f'{TXT.replace("╔📄 Moviendo archivos...", "╔ ✅ Tarea finalizada")}║\n╚➣ 📂 __{NAME_FOLDER}__',
                                  reply_markup=BUTTON_FILES)

            else:
                FILE = join(directory, DIC_FILES[username].get(int(NUM)))
                if isdir(FILE):
                    raise ValueError(
                        'El numero indicado no corresponde a un archivo')
                else:
                    if '/' in FOLDER:
                        NAME_FOLDER = directory.split("/")[-2]
                        move(FILE, directory.split("/")[-2])
                    else:
                        NAME_FOLDER = DIC_FILES[username].get(int(FOLDER))
                        FOLDER_INDEX = join(
                            directory, DIC_FILES[username].get(int(FOLDER)))
                        move(FILE, FOLDER_INDEX)

                    message.reply("✅ **Tarea finalizada**\n\n╔ 📄 __{}__\n║\n╚➣ 📂 __{}__".
                                  format(DIC_FILES[username].get(int(NUM)), NAME_FOLDER), reply_markup=BUTTON_FILES)

        except Exception as x:
            message.reply(f'__{x}__')

        # =============================== PICAR ARCHIVOS ===============================#

    elif SMS_TEXT.startswith("/split "):
        try:
            NUM = SMS_TEXT.split(" ")[1]
            if NUM.isdigit():
                FILE = DIC_FILES[username].get(int(NUM))
                if int(NUM) > len(listdir(path=directory)):
                    return message.reply('**⚠️ El número indicado no se encuentra en la lista**', reply_markup=BUTTON_BACK)
                SMS = message.reply(
                    f"✂️ **Dividiendo archivo: `{FILE}`\n📚 Tamaño de partes: `2000 MB`**")
                split(f'./{join(directory, FILE)}', f'./{username}', getBytes("2000.0MiB"))
                SMS.edit_text("**✅ Tarea finalizada con éxito**",
                              reply_markup=BUTTON_FILES)
            else:
                message.reply(
                    "**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/split 1`**", reply_markup=BUTTON_BACK)
            WORKING[username] = False
        except Exception as x:
            message.reply(x)

        # =============================== VER ARCHIVOS ===============================#

    elif SMS_TEXT.startswith("/files"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        saved_messages = showFiles(
            app, message,   saved_messages, directory, username)

    elif SMS_TEXT.startswith("/dl_"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        FILE = DIC_FILES[username].get(int(SMS_TEXT.replace('/dl_', '')))
        if isdir(f"{directory}/{FILE}"):
            rmtree(join(directory, FILE))
            saved_messages = showFiles(
                app, message,   saved_messages, directory, username)
        else:
            unlink(f"{directory}/{FILE}")
            saved_messages = showFiles(
                app, message,   saved_messages, directory, username)

    elif SMS_TEXT.startswith("/rn_"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except Exception as x:
            print(f"No se encuentra el mensaje: {x}")
        file = DIC_FILES[username].get(int(SMS_TEXT.replace('/rn_', '')))
        message.reply(
            f'**📝 Escriba un nuevo nombre para: `{file}`**', reply_markup=ForceReply())

        # =============================== CREAR CARPETA ===============================#

    elif SMS_TEXT.startswith("/mkdir"):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except Exception as x:
            print(f"No se encuentra el mensaje: {x}")
        FOLDER = SMS_TEXT.replace('/mkdir', "")
        FOLDER = normalize('NFKD', FOLDER).encode(
            'ascii', 'ignore').decode('utf-8', 'ignore')
        FOLDER = ''.join(c for c in FOLDER if ord(c) < 128)
        FOLDER = FOLDER[1:].replace(" ", "_")
        if FOLDER == "":
            return message.reply("**Debe escribir el comando, dejar un espacio, el nombre de la carpeta: \nEjemplo: `/mkdir Mi Carpeta`**")
        try:
            mkdir(join(directory, FOLDER))
        except FileExistsError:
            return message.reply("**⚠️ Ya existe una carpeta con ese nombre**")
        saved_messages = showFiles(
            app, message,   saved_messages, directory, username)

        # =============================== ELIMINAR ARCHIVOS SELECCIONADOS ===============================#

    elif SMS_TEXT.startswith('/borrar'):
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass

        Text = '**✅ ARCHIVOS ELIMINADOS:\n'
        for i in SMS_TEXT.replace('/borrar ', '').split(' '):
            if i.isdigit():
                FILE = DIC_FILES[username].get(int(i))
                if FILE == None:
                    message.reply(
                        f'**⚠️ ERROR: [`{i}`] No se encuentra en la lista**')
                else:
                    Text += f'\n🗑 `{FILE}`'
                    unlink(join(directory, FILE))

            else:
                message.reply(f'**⚠️ ERROR: [`{i}`] No es un numero**')
        message.reply(f'{Text}**', reply_markup=BUTTON_BACK)

        # =============================== COMPRIMIR ARCHIVOS ELEGIDOS ===============================#

    elif SMS_TEXT.startswith("/zip"):
        try:
            try:
                for i in saved_messages[username]["sms_files"]:
                    i.delete()
            except:
                pass
            text = "**📂 Archivos para comprimir: \n**"
            listCompress = []
            for i in SMS_TEXT.split(" ")[1:]:
                file = DIC_FILES[username].get(int(i))
                if file != None:
                    text += f"\n**{i}-** 📄 `{file}`\n"
                    listCompress.append(file)
                else:
                    text += f"\n**{i}-** __🚫 El archivo no se encuentra__\n"
            text += "\n**📝 Introduzca el nombre del zip\n🔑 Debajo una contraseña (Opcional)**"

            saved_messages[username] = {"listCompress": listCompress}
            message.reply(text, reply_markup=ForceReply())

        except Exception as x:
            print(x)
            message.reply(
                "**⚠️ Debe introducir los número correspondiente a los archivos a comprimir\n\nEjemplo: `/zip 1 4 8`**")

    # =============================== DESCOMPRIMIR ARCHIVO SELECCIONADO ===============================#

    elif SMS_TEXT.startswith("/unzip"):
        try:
            NUM = SMS_TEXT.split(" ")[1]
            if NUM.isdigit():
                FILE = DIC_FILES[username].get(int(NUM))
                if int(NUM) > len(listdir(path=directory)):
                    return message.reply('**⚠️ El número indicado no se encuentra en la lista**', reply_markup=BUTTON_BACK)
                if FILE.endswith('zip') == False and FILE.endswith('rar') == False and FILE.endswith('7z') == False:
                    return message.reply('**⚠️ El formato del archivo seleccionado no es compatible con la operación solicitada. Por favor, asegúrese de que el archivo tenga la extensión [`.zip`, `.rar`]**', reply_markup=BUTTON_BACK)
                SMS = message.reply(
                    f"♻️ **Descomprimiendo archivo: `{FILE}`**")

                if FILE.endswith('zip'):
                    with ZipFile(join(directory, FILE), 'r') as zip:
                        zip.extractall(directory)
                elif FILE.endswith('rar'):
                    with RarFile(join(directory, FILE)) as rf:
                        rf.extractall(directory)
                elif FILE.endswith('7z'):
                    with SevenZipFile(join(directory, FILE), mode='r') as z:
                        z.extractall(directory)

                sms.delete()
                saved_messages = showFiles(
                    app, message,   saved_messages, directory, username)
            else:
                message.reply(
                    "**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/split 1`**", reply_markup=BUTTON_BACK)
        except Exception as x:
            message.reply(x)
        
        #=============================== UNIRSE AL CANAL DE TELEGRAM ===============================#
    
    elif SMS_TEXT.startswith('https://t.me/') or SMS_TEXT.startswith('https://t.me/joinchat/'):
        if SMS_TEXT.split("/")[2] == "t.me" and SMS_TEXT.split("/")[-1].isdigit() == False and SMS_TEXT.endswith("?single") == False:
            msag = message.reply("**⌛️ ACCEDIENDO**")
            try:
                chat = userbot.join_chat(SMS_TEXT)
                id = chat.id
                msag.edit_text('**✅ ACCESO CONCEDIDO**')
            except (ChannelInvalid, InviteHashExpired, PeerIdInvalid):
                msag.edit_text('**🚫 ENLACE NO VÁLIDO**')
            except UserAlreadyParticipant:
                msag.edit_text('**⚠️ YA POSEE ACCESO**')
                
        return

# **************************************** GUARDAR ARCHIVOS PARA DESCARGAR **************************************** #

def download_files_telegram(username):
    global saved_messages
    global download_queues
    queue = download_queues[username]
    folder_files = {username:[]}
    try:
        mkdir(username)
    except:
        pass
    
    while not queue.empty():
        message, directory = queue.get()
        sms = message.reply('**🚛 Downloading...**', quote=True)
        start = tm()
        file = app.download_media(message=message, file_name=f'{directory}/', progress=progressddl, progress_args=(sms, start, queue.qsize()))
        folder_files[username].append(file.split("\\")[-1])
                    
        sms.edit_text('✅ **Finished**')
        queue.task_done()
    
    try:
        for i in saved_messages[username]["sms_files"]:
            i.delete()
    except: pass
    
    saved_messages = showFiles(app, message,   saved_messages, directory, username)
    del download_queues[username]
    
@app.on_message(filters.media & filters.private)
def Descargar_Archivos_De_Telegram(app, message):
    username = message.from_user.username
    try:
        for i in saved_messages[username]["sms_files"]:
            i.delete()
    except: pass
    
    try:
        directory = USER_ROOT[message.from_user.username]
    except:
        directory = f"{message.from_user.username}"
        
    file_info = (message, directory)
    
    if username in download_queues:
        download_queues[username].put(file_info)
    else:
        queue = cola()
        queue.put(file_info)
        download_queues[username] = queue
        download_files_telegram(username)

async def sendMessage():
    # -1001661991113 ID GRUPO
    try:
        await app.send_message(BOTUSER, "**🤖 BOT REINICIADO 🔄**")
    except Exception as x:
        print(x)

# ========================================================================================================== SERVER

server = web.Application()
server.router.add_get('/file/{route}/{file_name}', download_file)
server.add_routes([web.static('/static', 'static')])

# Ruta del Index
server.router.add_get('/', index)
# Ruta del Usuario
server.router.add_get('/{user}', usr_path)

server.router.add_post('/submit', submit_handler)

runner = web.AppRunner(server)

async def despertar(sleep_time=10 * 60):
    while True:
        
        await asyncsleep(sleep_time)
        async with ClientSession() as session:
            async with session.get(f'https://{NAME_APP}.onrender.com/' + "/Despiertate"):
                pass

async def run_server():
    await app.start()
    print('Bot Iniciado')
    await sendMessage()
    try: await userbot.start()
    except: print("No hay session string")
    print('User Bot Iniciado')
    await runner.setup()
    print('Iniciando Server')
    await web.TCPSite(runner, host='0.0.0.0', port=PORT).start()
    print('Server Iniciado')

if __name__ == '__main__':
    app.loop.run_until_complete(run_server())
    if not DEBUG:
        app.loop.run_until_complete(despertar())
    idle()
