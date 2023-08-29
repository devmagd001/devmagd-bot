import pytz
from shutil import rmtree, move
from UploadFiles import uploadFiles, uploadOnefile, compressfiles, compressSelectedFiles
from progrs import progressddl
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from unicodedata import normalize
from psutil import virtual_memory, disk_usage
from queue import Queue as cola
# from pyrogram.errors import ChannelBanned, ChannelInvalid,ChannelPrivate, ChatIdInvalid, ChatInvalid
# from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid,InviteHashExpired,usernameInvalid,UserAlreadyParticipant
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply, ReplyKeyboardRemove, InputMediaPhoto, InputMediaDocument, InputMediaVideo
from ModulesDownloads.youtubedl import YoutubeDL
from ModulesDownloads.compress import split, getBytes
from tools import cleanString, crearUsuario, download_of_youtube, comprobacion, download_youtube, extractInfoVideo, mostrar_opciones, showFiles, DIC_FILES, extractImg, sizeof, sendInfo
from asyncio import sleep as asyncsleep, Queue
from aiohttp import ClientSession
from aiohttp import web
from server import download_file, submit_handler, index, usr_path
from time import time as tm, gmtime, sleep
from datetime import datetime
from random import randint
from pyrogram.methods.utilities.idle import idle
from pyrogram.session import session
from pymongo import MongoClient
from Downloads import DownloadFiles
from os import listdir, mkdir, getenv, unlink, rename
from os.path import getsize, join, isdir, isfile, exists
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from uploadDrive import upload_to_tdd
from zipfile import ZipFile
from rarfile import RarFile
from py7zr import SevenZipFile
from pickle import dumps, loads
from requests import post, delete, get
from cv2 import resize, imread, imwrite
from json import dumps
from ModulesDownloads.file_tipeClass import fileType
from progrs import text_progres


session.Session.WAIT_TIMEOUT = 60

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
DATABASE = getenv("DATABASE")
NAME_APP = getenv("NAME_APP")
PORT = getenv('PORT')
SERVER = getenv('SERVER')
# SESSION_STRING = getenv('SESSION_STRING')

try:
    from Debug import DATABASE, BOT_TOKEN, PORT
    print("MODO DEBUG")
    DEBUG = True
except:
    print("MODO ONLINE")
    DEBUG = False

app = Client(name="rey_uploadpackBot", api_hash=API_HASH,
             api_id=API_ID, bot_token=BOT_TOKEN)
# userbot = Client("userbot", API_ID, API_HASH, bot_token=BOT_TOKEN, session_string=SESSION_STRING)

client = MongoClient(DATABASE, serverSelectionTimeoutMS=9999999)
UsersDB = client.MyDataBase
user_collection = UsersDB.UserInfo
free_users = UsersDB.FreeUsers
# =====================Variables Globales
saved_messages = {}
LISTA_ARCHIVOS = []
USER_ROOT = {}
CHOSE_FORMAT = {}
WORKING = {}
FECHA_INICIAL = datetime.now()
USERS = []
download_queues = {}
download_queues_url = {}

FREE_PASS = []
for i in free_users.find({}):
        FREE_PASS.append(i['username'])
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
    listfiles = f"**📆 Días restantes: {30 - user_collection.find_one({'username': query.from_user.username})['time_use']}**\n\n"
    listfiles += f"**📂 RUTA: `./{query.from_user.username}`**\n\n"
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
            await uploadOnefile(app, SMS, i, directory, user_collection, len(FOLDER_FILES), count)
    await SMS.reply_sticker("./assets/fin.webp")
    await stk.delete()


@app.on_callback_query(filters.create(lambda f, c, u: u.data == 'borrartodo'))
def borrar_todo(app, callback_query):
    global saved_messages
    username = callback_query.from_user.username
    SMS = callback_query.message
    try:
        directory = USER_ROOT[username]
    except:
        directory = f"{username}"

    try:
        for i in saved_messages[username]["sms_files"]:
            i.delete()
    except:
        pass

    for i in listdir(directory):
        if isfile(join(directory, i)):
            unlink(join(directory, i))

    saved_messages = showFiles(
        app, SMS, user_collection, free_users, saved_messages, directory, username)


@app.on_callback_query()
def callbackQuery(app, callback_query):
    global DIC_FILES
    global saved_messages
    global USER_ROOT
    global WORKING

    FREE_PASS = []
    for i in free_users.find({}):
        FREE_PASS.append(i['username'])

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
            app, SMS, user_collection, free_users, saved_messages, directory, username)

        # **************************************** RETROCEDER DIRECTORIO *********************************************

    elif CALLBACK_DATA == 'back':
        USER_ROOT[username] = "/".join(USER_ROOT[username].split('/')[:-1])
        try:
            directory = USER_ROOT[username]
        except:
            directory = username

        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        saved_messages = showFiles(
            app, SMS, user_collection, free_users, saved_messages, directory, username)

        # **************************************** ATRAS *********************************************

    elif CALLBACK_DATA == 'backk':
        SMS.delete()
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass

        saved_messages = showFiles(
            app, SMS, user_collection, free_users, saved_messages, directory, username)

        # **************************************** OPCIONES *********************************************

    elif CALLBACK_DATA == 'option':
        try:
            for i in saved_messages[username]["sms_files"]:
                i.delete()
        except:
            pass
        mostrar_opciones(SMS, user_collection, username)

        # **************************************** SUBIR ARCHIVO *********************************************

    elif CALLBACK_DATA == 'savedesc':
        MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton('✅ ACTIVAR', callback_data='saveon'),
                                       InlineKeyboardButton('☑️ DESACTIVAR', callback_data='saveoff')],
                                       [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
        SMS.edit_text('**Seleccione una opcion**', reply_markup=MARKUP)

    elif CALLBACK_DATA == 'saveon':
        user_collection.update_one({'username': username}, {
                                   "$set": {'savedesc': True}})
        SMS.edit_text("**Los archivos de Telegram se descargarán con el nombre que tenga en su descripción.**",
                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))

    elif CALLBACK_DATA == 'saveoff':
        user_collection.update_one({'username': username}, {
                                   "$set": {'savedesc': False}})
        SMS.edit_text("**☑️ DESACTIVADO**", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))

        # **************************************** SUBIR ARCHIVO *********************************************

    elif CALLBACK_DATA == 'upp':
        WORKING[username] = True
        FILE = callback_query.message.text.replace(
            "✅ DESCARGA FINALIZADA \n\n🔖 Nombre: ", "").split("\n")[0]
        # uploadOnefile(app, SMS, FILE, directory, user_collection, 1, 1)
        WORKING[username] = False

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
        markup = InlineKeyboardMarkup([[InlineKeyboardButton('ZIP', callback_data='zip'),
                                       InlineKeyboardButton('7z', callback_data='7z')],
                                       [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='option')]])
        SMS.edit_text('**📚 Elige el formato de compresión **',
                      reply_markup=markup)

    elif CALLBACK_DATA == "zip" or CALLBACK_DATA == "7z":
        SMS.edit_text(
            f"**✅ Done, the format will be: `{CALLBACK_DATA}`**", reply_markup=BUTTON_BACK)
        user_collection.update_one({'username': username}, {
                                   "$set": {'compression_format': CALLBACK_DATA}})

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
        user_collection.update_one({'username': username}, {
                                   "$set": {'autoUpload': 'up_compress'}})
        SMS.edit_text("📦 **Los archivos se subirán comprimidos**",
                      reply_markup=BUTTON_BACK)

    elif CALLBACK_DATA == "up_noCompress":
        user_collection.update_one({'username': username}, {
                                   "$set": {'autoUpload': 'up_noCompress'}})
        SMS.edit_text("📄 **Los archivos se subirán sin comprimir**",
                      reply_markup=BUTTON_BACK)

    elif CALLBACK_DATA == "desactivate":
        user_collection.update_one({'username': username}, {
                                   "$set": {'autoUpload': False}})
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

    # **************************************** ESCRIBIR CAPTION ****************************************#

    elif CALLBACK_DATA == 'caption':
        SMS.delete()
        try:
            DESCAP = loads(user_collection.find_one(
                {'username': username})['caption'])
        except:
            DESCAP = 'None'
        msg = '**📝 Escriba el texto que desea que se incluya en los archivos subidos por el Bot:**'
        msg += '**\n\n💬 Texto actual:**\n'
        SMS.reply(msg, reply_markup=ForceReply())
        if DESCAP != 'None':
            MSGD = SMS.reply(f'{DESCAP["text"]}', entities=DESCAP['entities'], reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('🚮 BORRAR ', callback_data='eliminarCaption')]]))
            saved_messages[username] = {"sms_caption": MSGD}

    elif CALLBACK_DATA == 'eliminarCaption':
        SMS.delete()
        user_collection.update_one({'username': username}, {
                                   "$set": {'caption': 'None'}})
        SMS.reply('✅', reply_markup=BUTTON_BACK)

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
        user_collection.update_one({'username': username}, {
                                   "$set": {'video_format': 'Video'}})
        SMS.edit_text("**🎞 VIDEO**", reply_markup=BUTTON_BACK)
    elif CALLBACK_DATA == 'Documento':
        user_collection.update_one({'username': username}, {
                                   "$set": {'video_format': 'Documento'}})
        SMS.edit_text("**📄 DOCUMENTO**", reply_markup=BUTTON_BACK)

# ******************************************************************************************************** #
# ******************************************* RESPONDER MENSAJES ***************************************** #
# ******************************************************************************************************** #


@app.on_message(filters.command('add_buttons') & filters.reply)
def Agregar_botones(app, message):
    global saved_messages
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
    await uploadFiles(app, message, message.text, directory, FOLDER_FILES, user_collection)


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
            user_collection.update_one({'username': username}, {
                                       "$set": {'file_thumb': id_doc.document.file_id}})
        except Exception as x:
            return message.reply(f"🚫 **Ah ocurrido un error\n{x}** 🚫", reply_markup=BUTTON_BACK)
        return

    # =============================== CARGAR TXT ===============================#

    try:
        if message.text.startswith("/loadusers"):
            if SMS_REPLY.document.mime_type == "text/plain":
                if username == "ErickYasser" or username == "KOD_16":
                    free_userss = []
                    for i in free_users.find({}):
                        free_userss.append(i['username'])
                    file = SMS_REPLY.download(file_name="./")
                    txt = "**Usuarios Añadidos: \n"
                    with open(file, 'r') as f:
                        for i in f.read().split('\n'):
                            if i.split("=")[0] not in free_userss:
                                nm = i.split("=")[0]
                                free_users.insert_one({'username': nm})
                                txt += f"👤 @{nm}\n"
                    txt += "**"
                    unlink(file)
                    message.reply(txt)
                    return

        if message.text.startswith("/delusers"):
            if SMS_REPLY.document.mime_type == "text/plain":
                if username == "ErickYasser" or username == "KOD_16":
                    free_userss = []
                    for i in free_users.find({}):
                        free_userss.append(i['username'])
                    file = SMS_REPLY.download(file_name="./")
                    txt = "**Usuarios Eliminados: \n"
                    with open(file, 'r') as f:
                        for i in f.read().split('\n'):
                            if i in free_userss:
                                nm = i.split("=")[0]
                                free_users.delete_one({'username': nm})
                                txt += f"🚷 @{nm}\n"

                    txt += "**"
                    unlink(file)
                    message.reply(txt)
                    return

        if message.text.startswith("/loadtxt"):
            if SMS_REPLY.document.mime_type == "text/plain":
                fl = SMS_REPLY.download(file_name="./")
                with open(fl, 'r') as txt:
                    for i in txt.read().split("\n"):
                        print(i)
            return
    except:
        pass

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

           # =============================== AÑADIR CAPTION ===============================#

    elif SMS_REPLY.text.startswith('📝 Escriba el texto que desea que se incluya en los archivos subidos por el Bot:'):
        if len(message.text) > 1024:
            return message.reply('**⚠️ El mensaje enviado es demasiado largo**', reply_markup=BUTTON_BACK)
        CAPTION_D = dumps({'text': message.text, 'entities': message.entities})
        user_collection.update_one({'username': username}, {
                                   "$set": {'caption': CAPTION_D}})
        message.reply('✅', reply_markup=BUTTON_BACK)
        try:
            saved_messages[username]["sms_caption"].delete()
        except:
            pass
        SMS_REPLY.delete()

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
        WORKING[username] = True
        SMS_REPLY.delete()
        message.delete()
        compressfiles(app, message, message.text, directory, user_collection)
        message.reply("**✅ COMPRESION FINALIZADA**", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('📬 ARCHIVOS 📬', callback_data='ver')]]))
        WORKING[username] = False

        # =============================== ZIPS SIZE ===============================#

    elif SMS_REPLY.text == '📚 Introduzca el tamaño de los zips:':
        try:
            zips = int(message.text)
            if zips >= 1 and zips <= 2000:
                user_collection.update_one({'username': username}, {
                                           "$set": {'zip_size': zips}})
                message.reply(
                    f"✅ **Zips establecidos en: [ `{zips} MB` ]**", reply_markup=BUTTON_BACK)
            else:
                message.reply(
                    '❌ **Debes introducir un número entre 1 y 2000**', reply_markup=BUTTON_BACK)
        except ValueError:
            message.reply('❌ **Debes introducir solo números**',
                          reply_markup=BUTTON_BACK)

        # =============================== COMPRIMIR ARCHIVOS ESCOGIDOS ===============================#

    elif SMS_REPLY.text.startswith("📂 Archivos para comprimir: "):
        WORKING[username] = True
        SMS_REPLY.delete()
        message.delete()
        compressSelectedFiles(message, message.text, username,
                              saved_messages[username]["listCompress"], user_collection, directory)
        message.reply("**✅ Compresión realizada**", reply_markup=BUTTON_BACK)
        WORKING[username] = False

# ******************************************************************************************************** #
# ******************************************* RECIBIR MENSAJES ******************************************* #
# ******************************************************************************************************** #

@app.on_message(filters.command(['logs', 'restart']) & filters.user(['KOD_16', 'ErickYasser', 'FileMaster_Service']))
def Administrador(app, message):
    """
    La función `Administrador` es una función de Python que maneja comandos relacionados con el reinicio
    de dynos y la recuperación de registros para una aplicación Heroku.

    :param app: El parámetro `app` es el nombre de la aplicación Heroku que desea administrar. En este
    caso, el nombre de la aplicación es "filemaster"
    :param message: El parámetro `mensaje` es el mensaje de entrada recibido por la función. Se utiliza
    para determinar la acción a realizar por la función `Administrador`
    """
    response = 0
    api_key = "e8bb7e45-fe67-4e01-92a6-fb76b63ccd15"
    headers = {
        "Accept": "application/vnd.heroku+json; version=3",
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if message.text.startswith('/restart'):
        url = f"https://api.heroku.com/apps/{NAME_APP}/dynos"
        response = delete(url, headers=headers)
        if response.status_code == 202:
            message.reply('**Dyno restarted successfully**')
        else:
            message.reply(f'**Error restarting dyno: {response.status_code}**')

    elif message.text.startswith('/logs'):
        url = f"https://api.heroku.com/apps/{NAME_APP}/log-sessions"
        response = post(url, headers=headers)
        log_url = response.json()["logplex_url"]
        logs_response = get(log_url, headers=headers, stream=True)
        log = ""
        for line in logs_response.iter_lines():
            if line:
                log += line.decode("utf-8").split(':')[-1] + '\n\n'
        message.reply(f'**{log}**')


@app.on_message(filters.regex('/up_') & ~ filters.regex('/up_all') & ~ filters.regex('/up_album'))
async def subirArchivo(app, message):
    """
    La función `subirArchivo` se usa para cargar un archivo en un chat de Telegram, con algunas
    comprobaciones adicionales de privilegios de usuario.

    :param app: El parámetro "aplicación" es probablemente una instancia de la aplicación o marco en el
    que se ejecuta este código. Se utiliza para acceder a la funcionalidad necesaria para cargar
    archivos
    :param message: El parámetro `message` es un objeto que representa el mensaje enviado por el
    usuario. Contiene información como el remitente, el texto del mensaje y cualquier archivo o medio
    adjunto
    :return: nada (Ninguno).
    """
    global saved_messages
    FREE_PASS = []
    for i in free_users.find({}):
        FREE_PASS.append(i['username'])

    if not user_collection.find_one({'username': message.from_user.username})["user_vip"] and message.from_user.username not in FREE_PASS:
        return

    try:
        for i in saved_messages[message.from_user.username]["sms_files"]:
            await i.delete()
    except:
        pass

    FILE_NAME = DIC_FILES[message.from_user.username].get(
        int(message.text.replace('/up_', '')))
    try:
        directory = USER_ROOT[message.from_user.username]
    except:
        directory = f"{message.from_user.username}"
    await uploadOnefile(app, message, FILE_NAME, directory, user_collection, 1, 1)


@app.on_message(filters.command('status'))
async def estadoBot(app, message):
    """
    La función `estadoBot` recupera y muestra información sobre el uso de almacenamiento y RAM del
    sistema, así como el tiempo activo del bot.

    :param app: El parámetro `app` es probablemente una instancia de la aplicación o marco en el que se
    ejecuta el código. Se utiliza para interactuar con la aplicación y realizar diversas tareas
    :param message: El parámetro `message` es el objeto de mensaje que contiene información sobre el
    mensaje que activó la función. Incluye detalles como el remitente, el contenido del mensaje y otros
    metadatos
    """
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
    sms = await message.reply(TXT)


@app.on_message(filters.command('up_album'))
async def subirAlbum(app, message):
    """
    La función `subirAlbum` sube una colección de fotos, videos y documentos a un chat usando la API de
    Telegram.

    :param app: El parámetro "aplicación" es una instancia de la aplicación o bot que maneja el mensaje.
    Se utiliza para enviar y recibir mensajes, pegatinas, medios, etc
    :param message: El parámetro `mensaje` es un objeto que representa el mensaje recibido por la
    aplicación. Contiene información como el remitente, el chat al que fue enviado, el contenido del
    mensaje, etc
    :return: nada.
    """
    FREE_PASS = []
    for i in free_users.find({}):
        FREE_PASS.append(i['username'])

    if not user_collection.find_one({'username': message.from_user.username})["user_vip"] and message.from_user.username not in FREE_PASS:
        return

    try:
        directory = USER_ROOT[message.from_user.username]
    except:
        directory = f"{message.from_user.username}"
    try:
        for i in saved_messages[message.from_user.username]["sms_files"]:
            await i.delete()
    except:
        pass
    stk = await message.reply_sticker("./assets/subiendo.tgs")
    FOLDER_FILES = listdir(directory)
    FOLDER_FILES.sort()
    ListPhotos = []
    ListVideo = []
    ListDocument = []
    if exists(f"./{message.from_user.username}-thumb.jpg"):
        thumb = f"./{message.from_user.username}-thumb.jpg"
    else:
        thumb = "./assets/thumb.jpg"
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

@app.on_message(filters.command('sms_all') & filters.user(['KOD_16', 'FileMaster_Service']))
async def enviarMensajeGlobal(app, message):
    """
    La función `enviarMensajeGlobal` envía un mensaje global a todos los usuarios de una colección,
    utilizando sus ID de usuario, y devuelve un mensaje de confirmación cuando se completa la tarea.

    :param app: El parámetro "aplicación" es una instancia de la aplicación o bot que se utiliza para
    enviar mensajes. Se utiliza para llamar al método "send_message" para enviar mensajes a los usuarios
    :param message: El parámetro `message` es el objeto de mensaje que contiene el texto y otra
    información del mensaje recibido por el bot
    """
    mensaje = message.text.replace("/sms_all", "")
    user = user_collection.find()
    for i in user:
        try:
            await app.send_message(i['user_id'], mensaje)
        except:
            pass

    await message.reply('TAREA FINALIZADA')


@app.on_message(filters.command('extractimg'))
async def extraer_imagenes(app, message):
    """
    La función `extraer_imagenes` extrae imágenes de un archivo de video y las envía como un grupo de
    medios en un chat de Telegram.

    :param app: El parámetro "aplicación" es una instancia de la aplicación o marco que se utiliza para
    manejar el mensaje entrante. Se utiliza para interactuar con la plataforma de mensajería y enviar
    respuestas al usuario
    :param message: El parámetro `mensaje` es un objeto que representa el mensaje entrante del usuario.
    Contiene información como el texto del mensaje, el usuario que envió el mensaje y otros metadatos
    """
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
            else:
                await message.reply(
                    "⚠️ El archivo seleccionado no es un video válido")
        else:
            await message.reply(
                "**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/extractimg 1`**")
    except Exception as x:
        print(x)
        rmtree(message.from_user.username + "/IMG")
        await message.reply(
            "**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/extractimg 1`**")

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
        try: DownloadFiles(app, message, url, username, user_collection, directory, format, queue.qsize())
        except Exception as x:message.reply(x)
        queue.task_done()
        
    saved_messages = showFiles(app, message, user_collection, free_users, saved_messages, directory, username)
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
    crearUsuario(app, message, username, user_collection, free_users)
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

    freePass = []
    for i in free_users.find({}):
        freePass.append(i['username'])

    if username == "KOD_16" or username == "FileMaster_Service":
        if SMS_TEXT.startswith("@"):
            username = SMS_TEXT[1:]
            TXT = ''
            duser = user_collection.find_one({'username': username})
            for i in duser.items():
                TXT += f'**{i[0]}: **{str(i[1])}\n'
            message.reply(TXT)
            return

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

También le sugiero que se una a estos enlaces, donde podrá encontrar información relevante y comunicarse con otros usuarios:

● [Canal](https://t.me/ReyBots_support) 📢
● [Grupo](https://t.me/ReyBots_supportChat) 💬
● [Tutoriales](https://t.me/Tutorial_DownloadPack) 🎥

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

        mostrar_opciones(message, user_collection, username)

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
            app, message, user_collection, free_users, saved_messages, directory, username)

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
        # if WORKING:
        #     message.reply('**⏱ El Bot ya tiene un proceso activo, por favor espere...**')
        # else:
        #     WORKING[username] = True
        try:
            NUM = SMS_TEXT.split(" ")[1]
            if NUM.isdigit():
                FILE = DIC_FILES[username].get(int(NUM))
                if int(NUM) > len(listdir(path=directory)):
                    return message.reply('**⚠️ El número indicado no se encuentra en la lista**', reply_markup=BUTTON_BACK)
                SMS = message.reply(
                    f"✂️ **Dividiendo archivo: `{FILE}`\n📚 Tamaño de partes: `{user_collection.find_one({'username':username})['zip_size']} MB`**")
                split(f'./{join(directory, FILE)}', f'./{username}', getBytes(
                    f"{user_collection.find_one({'username':username})['zip_size']}.0MiB"))
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
            app, message, user_collection, free_users, saved_messages, directory, username)

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
                app, message, user_collection, free_users, saved_messages, directory, username)
        else:
            unlink(f"{directory}/{FILE}")
            saved_messages = showFiles(
                app, message, user_collection, free_users, saved_messages, directory, username)

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
            app, message, user_collection, free_users, saved_messages, directory, username)

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
                    app, message, user_collection, free_users, saved_messages, directory, username)
            else:
                message.reply(
                    "**⚠️ Debe introducir el número correspondiente al video\n\nEjemplo: `/split 1`**", reply_markup=BUTTON_BACK)
        except Exception as x:
            message.reply(x)

           # =============================== AÑADIR VIP ===============================#

    elif SMS_TEXT.startswith("/addvip"):
        if username == "FileMaster_Service" or username == "KOD_16":
            try:
                username = SMS_TEXT.split(' ')[-1]
                if username.startswith('@'):
                    username = username[1:]
                user = app.get_users(username)
                user_collection.update_one({'username': username}, {
                                           "$set": {'time_use': [0, 0, 0]}})
                user_collection.update_one({'username': username}, {
                                           "$set": {'user_vip': True}})
                user_collection.update_one({'username': username}, {"$set": {'date_join': [
                                           gmtime(tm()).tm_mday, gmtime(tm()).tm_mon, gmtime(tm()).tm_year]}})
            except Exception as x:
                print(x)

            message.reply(
                f'**Usuario: @{username} TIENE ACCESO: {user_collection.find_one({"username":username})["user_vip"]}**')
            app.send_sticker(user.id, "./assets/acc.tgs")
            app.send_message(
                user.id, "**🔓 SE LE HA CONCEDIDO EL ACCESO AL BOT\n\nℹ️ __Cualquier duda o sugerencia Contactar a :\n👤 @FileMaster_Service__**")

            # =============================== QUITAR VIP ===============================#

    elif SMS_TEXT.startswith("/delvip"):
        if username == "UploadPack" or username == "KOD_16":
            username = SMS_TEXT.split(' ')[-1]
            if username.startswith('@'):
                username = username[1:]
            user_collection.update_one({'username': username}, {
                                       "$set": {'user_vip': False}})
            message.reply(f'**Usuario: @{username} NO TIENE ACCESO**')

            # =============================== VER USUARIOS ===============================#

    elif SMS_TEXT.startswith("/users"):
        if username == 'KOD_16' or username == 'ErickYasser':
            txt = "Usuarios con libre acceso:\n"
            dates = set()
            for i in free_users.find():
                dates.add(i['date_join'])
            
            for date in dates:
                txt += f'\n● {date}\n'
                for i in free_users.find({}):
                    if i['date_join'] == date:
                        txt += f"@{i['username']}\n"
                    
            with open("Usuarios.txt", "w", encoding='UTF-8') as user:
                user.write(txt)
            try:
                message.reply(f"**{txt}**")
                message.reply_document("Usuarios.txt")
            except:
                message.reply_document("Usuarios.txt")

            # =============================== ELIMINAR USUARIOS ===============================#

    elif SMS_TEXT.startswith("/deluser"):
        if username == 'KOD_16' or username == 'ErickYasser':
            delusr = SMS_TEXT.replace("/deluser", "").split(" ")
            txt = "**Usuarios Eliminados: **\n"
            for i in delusr:
                if len(i) > 1:
                    if i.startswith('@'):
                        i = i[1:]
                    free_users.delete_one({'username': i})
                    txt += f"🚷** @{i}**\n"
            message.reply(txt)

            # =============================== AÑADIR USUARIOS ===============================#

    elif SMS_TEXT.startswith("/adduser"):
        if username == 'KOD_16' or username == 'ErickYasser':
            addusr = SMS_TEXT.replace("/adduser", "").split(" ")
            txt = "**Usuarios Añadidos: **\n"
            li = []
            for i in free_users.find():
                li.append(i['username'])

            for i in addusr:
                if len(i) > 1:
                    if i.startswith('@'):
                        i = i[1:]
                    if i not in li:
                        fecha_actual = datetime.now(pytz.timezone('America/Havana'))
                        free_users.insert_one({'username': i,
                                               'date_join': fecha_actual.strftime("%d/%m/%Y")})
                      
                        txt += f"👤** @{i}**\n"
                    else:
                        return message.reply(f"**El usuario @{i} ya se encuentra en la base de datos**")
            message.reply(txt)
        
    #     #=============================== UNIRSE AL CANAL DE TELEGRAM ===============================#
    # elif message.text.split("/")[2] == "t.me" and message.text.split("/")[-1].isdigit() == False and message.text.endswith("?single") == False:
    #     if user_collection.find_one({'username':username})['supervip'] or username in freePass:
    #         if message.text.startswith('https://t.me/') or message.text.startswith('https://t.me/joinchat/'):
    #             if username == "ErickYasser" or username == "KOD_16":
    #                 msag = message.reply("**⌛️ ACCEDIENDO**")
    #                 try:
    #                     chat = userbot.join_chat(message.text)
    #                     id = chat.id
    #                     msag.edit_text('**✅ ACCESO CONCEDIDO**')
    #                 except (usernameInvalid, ChannelInvalid, InviteHashExpired, PeerIdInvalid):
    #                     msag.edit_text('**🚫 ENLACE NO VÁLIDO**')
    #                 except UserAlreadyParticipant:
    #                     msag.edit_text('**⚠️ YA POSEE ACCESO**')
    #             else:
    #                 return message.reply("**⚠️ Debe enviar el enlace a @KOD_16 para ser revisado y aprobado**")

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
        if user_collection.find_one({'username': username})['savedesc']:
            if message.caption == None:
                file = app.download_media(message=message, file_name=f'{directory}/', progress=progressddl, progress_args=(sms, start, queue.qsize()))
                folder_files[username].append(file.split("\\")[-1])
            else:
                caption = cleanString(String=message.caption.split('\n')[0])
                file = app.download_media(message=message, file_name=f'{directory}/', progress=progressddl, progress_args=(sms, start, queue.qsize()))
                rename(join(directory, file), join(directory, caption+file[-4:]))
                folder_files[username].append(caption+file[-4:].split("\\")[-1])
        else:
            file = app.download_media(message=message, file_name=f'{directory}/', progress=progressddl, progress_args=(sms, start, queue.qsize()))
            folder_files[username].append(file.split("\\")[-1])
                    
        sms.edit_text('✅ **Finished**')
        queue.task_done()
        
    if user_collection.find_one({'username': username})['user_vip'] == True or username in FREE_PASS:
        if user_collection.find_one({'username': username})["autoUpload"] == "up_compress":
            NM_ZIP = directory.split("/")[-1] + str(randint(100, 200))
            uploadFiles(app, message, NM_ZIP, directory, folder_files[username], user_collection)
        elif user_collection.find_one({'username': username})["autoUpload"] == "up_noCompress":
            count = 0
            for i in folder_files[username]:
                count += 1
                uploadOnefile(app, message, i, directory, user_collection, len(folder_files[username]), count)

    try:
        for i in saved_messages[username]["sms_files"]:
            i.delete()
    except: pass
    
    saved_messages = showFiles(app, message, user_collection, free_users, saved_messages, directory, username)
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
        await app.send_message("KOD_16", "**🤖 BOT REINICIADO 🔄**")
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
            async with session.get(f'https://{NAME_APP}.{SERVER}.com/' + "/Despiertate"):
                pass

async def run_server():
    await app.start()
    print('Bot Iniciado')
    await sendMessage()
    # Iniciando User Bot
    # await userbot.start()
    # print('User Bot Iniciado')
    await runner.setup()
    print('Iniciando Server')
    await web.TCPSite(runner, host='0.0.0.0', port=PORT).start()
    print('Server Iniciado')

if __name__ == '__main__':
    app.loop.run_until_complete(run_server())
    if not DEBUG:
        app.loop.run_until_complete(despertar())
    idle()
