from unicodedata import normalize
from cv2 import VideoCapture, resize, addWeighted, putText, imwrite, FONT_HERSHEY_SIMPLEX, CAP_PROP_FRAME_COUNT, CAP_PROP_POS_FRAMES, CAP_PROP_FPS
from os import listdir, mkdir, getenv, rename, unlink, makedirs, stat
from os.path import join, getsize, isfile, isdir, basename, splitext
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from time import sleep, time, localtime, strftime, gmtime
from ModulesDownloads.youtubedl import YoutubeDL
from progrs import progressytdl, progresstwitch
from subprocess import call
from unicodedata import normalize
from random import randint
from requests import get
from encrypt import cryptoKey

DIC_FILES = {}
NAME_APP = getenv("NAME_APP")
SERVER = getenv('SERVER')


def download_of_youtube(message, each, bot, url, DIRECTORY):
    """
    Esta función se encarga de separar los links de Twitch o Youtube o cualquier otra
    enlace de video, como Facebook entre otros
    """
    # La variable each contiene una lista con 3 valores: ['22', '1280x720 (720p)', 'mp4']
    # El método "YoutubeDL().info(url)" devuelve una lista con todos los formatos soportados para descargar el video
    # try:
    if 'twitch' in url:
        if "CallbackQuery" in str(message).split(':')[1]:
            MSG = message.message
            MSG.edit('**📥 Downloading from Twitch**')
        else:
            MSG = message.reply('**📥 Downloading from Twitch**')
        print("DESCARGANDO DE TWITCH")
        ytdl = YoutubeDL(progresstwitch, MSG, bot, True)
    elif 'youtu' in url:
        if "CallbackQuery" in str(message).split(':')[1]:
            MSG = message.message
            MSG.edit('**📥 Downloading Video**')
        else:
            MSG = message.reply('**📥 Downloading Video**')
        print("DESCARGANDO DE YOUTUBE")
        ytdl = YoutubeDL(progressytdl, MSG, bot, False)
    else:
        if "CallbackQuery" in str(message).split(':')[1]:
            MSG = message.message
            MSG.edit('**📥 Downloading Video...**')
        else:
            MSG = message.reply('**📥 Downloading Video...**')
        print("DESCARGANDO VIDEO")
        ytdl = YoutubeDL(progresstwitch, MSG, bot, True)

    file = ytdl.download(url, DIRECTORY, each[0])
    file = f"{file[:-4]}.{each[2]}"
    MSG.delete()
    if file.endswith('.m4a'):
        # Esta condición convierte el archivo en formato .any(iterable)mp3
        command = f"ffmpeg -i {file} -acodec libmp3lame -ab 320k {file[:-4]}.mp3"
        call(command, shell=True)
        unlink(file)
        file = file[:-4] + '.mp3'

    return file
    # except Exception as e:
    # msg.delete()
    # bot.send_message(msg.chat.id,f'❌**Video download failed.**❌ {e}')
    # return False


def sumar(a, b):
    return a - b


def crearUsuario(app, message, username, USER_COLLECTION, FREE_USERS):
    freePass = []
    for i in FREE_USERS.find({}):
        freePass.append(i['username'])

    if USER_COLLECTION.find_one({'username': username}) == None:
        USER_COLLECTION.insert_one({
            'username': username,
            'user_id': message.from_user.id,
            'send_link': True,
            'user_vip': False,
            'autoUpload': 'up_compress',
            'ban_user': False,
            'compression_format': 'zip',
            'youtube_format': ['22', '1280x720 (720p)', 'mp4'],
            'twitch_format': ['1080p60', ' 1920x1080 (Source)', 'mp4'],
            'date_join': [gmtime(time()).tm_mday, gmtime(time()).tm_mon, gmtime(time()).tm_year],
            'last_use': [0, 0, 0],
            'time_use': [0, 0, 0],
            'file_thumb': 'BQACAgEAAxkDAAIeWmMT7y4sQ6zeL_Yqs8QZpPsuAhKKAAJNBAACHBShRO2_9RU9hjDHHgQ',
            'zip_size': 2000,
            'number_use': 0,
            'total_upload': 0,
        })

    USER_COLLECTION.update_one({'username': username}, {"$set": {'last_use': [
                               gmtime(time()).tm_mday, gmtime(time()).tm_mon, gmtime(time()).tm_year]}})
    date_join = USER_COLLECTION.find_one({'username': username})['date_join']
    last_use = USER_COLLECTION.find_one({'username': username})['last_use']
    if last_use[1] != date_join[1]:
        result = last_use[0] + (30 - date_join[0])
    else:
        result = list(map(sumar, last_use, date_join))[0]

    USER_COLLECTION.update_one({'username': username}, {
                               "$set": {'time_use': result}})

    try:
        USER_COLLECTION.find_one({'username': username})['video_format']
    except:
        USER_COLLECTION.update_one({'username': username}, {
                                   "$set": {'video_format': 'Video'}})

    try:
        USER_COLLECTION.find_one({'username': username})['savedesc']
    except:
        USER_COLLECTION.update_one({'username': username}, {
                                   "$set": {'savedesc': False}})

    try:
        USER_COLLECTION.find_one({'username': username})['supervip']
    except:
        USER_COLLECTION.update_one({'username': username}, {
                                   "$set": {'supervip': False}})

    try:
        USER_COLLECTION.find_one({'username': username})['caption']
    except:
        USER_COLLECTION.update_one({'username': username}, {
                                   "$set": {'caption': 'None'}})

    if not USER_COLLECTION.find_one({'username': username})["user_vip"]:
        try:
            USER_COLLECTION.find_one({'username': username})['muestraGratis']
        except:
            USER_COLLECTION.update_one({'username': username}, {
                                       "$set": {'muestraGratis': True}})

        try:
            USER_COLLECTION.find_one({'username': username})['muestraProbada']
        except:
            USER_COLLECTION.update_one({'username': username}, {
                                       "$set": {'muestraProbada': False}})

    if username not in freePass:
        if USER_COLLECTION.find_one({'username': username})["user_vip"]:
            if USER_COLLECTION.find_one({'username': username})["time_use"] >= 30:
                app.send_message(
                    1231106365, f"**Usuario: @{username} SIN ACCESO**")
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'user_vip': False}})
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'supervip': False}})
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'time_use': 0}})
                USER_COLLECTION.update_one({'username': username}, {"$set": {'date_join': [
                                           gmtime(time()).tm_mday, gmtime(time()).tm_mon, gmtime(time()).tm_year]}})
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'total_upload': 0}})
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'muestraGratis': False}})
        else:
            if USER_COLLECTION.find_one({'username': username})["muestraProbada"] == False:
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'time_use': 0}})
                USER_COLLECTION.update_one({'username': username}, {"$set": {'date_join': [
                                           gmtime(time()).tm_mday, gmtime(time()).tm_mon, gmtime(time()).tm_year]}})
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'muestraProbada': True}})

            if USER_COLLECTION.find_one({'username': username})["time_use"] >= 2:
                USER_COLLECTION.update_one({'username': username}, {
                                           "$set": {'muestraGratis': False}})


async def comprobacion(app, message, username, USER_COLLECTION):
    if USER_COLLECTION.find_one({'username': username})["user_vip"] == False and USER_COLLECTION.find_one({'username': username})["muestraGratis"] == False:
        TXT = '**🔓 GET 30 DAY ACCESS:\n ● 50 CUP\n ● 1 USDT or equivalent\n\n**'
        TXT += '💳 **TARJETA CUP:** `9238-1299-7234-5971`\n'
        TXT += '💰 **CRYPTO:** https://bit.ly/3J3pHMA'
        TXT += '\n\n**__📲 [Send payment capture here](https://t.me/FileMaster_Service)__**'
        TXT += '\n**__📲 [Enviar captura del pago aquí](https://t.me/FileMaster_Service)__**'
        return await message.reply(TXT,  disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ℹ️ TUTORIAL ℹ️", url="https://t.me/Tutorial_DownloadPack")]])
        )
    return True


def showFiles(app, SMS, USER_COLLECTION, FREE_USERS, SAVED_MESSAGES, DIRECTORY, username):
    global DIC_FILES
    FREE_PASS = []
    for i in FREE_USERS.find({}):
        FREE_PASS.append(i['username'])

    if NAME_APP == None:
        LINK = f'http://localhost.8000/{cryptoKey().encriptar(texto=username)}'
        print(cryptoKey().encriptar(texto=username))
    else:
        LINK = f'https://{NAME_APP}.{SERVER}.com/{cryptoKey().encriptar(texto=username)}'
        
    if USER_COLLECTION.find_one({'username': username})["user_vip"] or username in FREE_PASS:
        MENU = InlineKeyboardMarkup([[InlineKeyboardButton('📦 SUBIR', callback_data='upload'), 
                                      InlineKeyboardButton('🗜 COMPRIMIR', callback_data='compres')],
                                     [InlineKeyboardButton('📤 SUBIR TODO', callback_data='up_all'), 
                                      InlineKeyboardButton('🗑 ELIMINAR TODO', callback_data='borrartodo')],
                                     [InlineKeyboardButton('⚙️ OPCIONES', callback_data='option'),
                                      InlineKeyboardButton('📂 ARCHIVOS', url=LINK)]])

    else:
        MENU = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                '⚜️ GET VIP', url='https://t.me/FileMaster_Service'),
            InlineKeyboardButton('🗜 COMPRIMIR', callback_data='compres')],
            [InlineKeyboardButton('⚙️ OPCIONES', callback_data='option')]])

    try:
        mkdir(username)  # CREAR CARPETA
    except:
        pass

    DIC_ARCH = {}
    TIME_USE = USER_COLLECTION.find_one({'username': username})['time_use']

    if 30 - TIME_USE > 1:
        listfiles = f"**📆 Días restantes: {30 - TIME_USE}**\n\n"
    else:
        listfiles = f"**📆 Días restantes: {30 - TIME_USE} ⚠️\n\n**"

    if len(DIRECTORY.split('/')) > 1:
        MENU = InlineKeyboardMarkup([[InlineKeyboardButton('⬅️', callback_data='back')],
                                     [InlineKeyboardButton('📦 SUBIR', callback_data='upload'),
                                      InlineKeyboardButton('🗜 COMPRIMIR', callback_data='compres')],
                                     [InlineKeyboardButton('⚙️ OPCIONES', callback_data='option')]])

    fileSize = 0
    try:
        FOLDER_FILES = listdir(DIRECTORY)
        listfiles += f"**📂 RUTA: `./{DIRECTORY}`**\n\n"
    except:
        FOLDER_FILES = listdir(username)
        listfiles += f"**📂 RUTA: `./{username}`**\n\n"

    FOLDER_FILES.sort()
    count = 0
    LSFILES = []
    for i in FOLDER_FILES:
        count = count + 1

        if count % 25 == 0:
            LSFILES.append(listfiles)
            listfiles = f"**🏷 RUTA: `./{DIRECTORY}`**\n\n"

        if isfile(f'{DIRECTORY}/{i}'):
            TXT = normalize('NFKD', i).encode(
                'ascii', 'ignore').decode('utf-8', 'ignore')
            CN = ''.join(c for c in TXT if ord(c) < 128)
            CN = CN.replace(" ", "_").replace('(', '').replace(')', '')

            rename(f"{DIRECTORY}/{i}", f"{DIRECTORY}/{CN}")
            LINK = f'https://{NAME_APP}.{SERVER}.com/file/{DIRECTORY}/{CN}'
            SIZE = round(getsize(join(DIRECTORY, CN)) / 1000024, 2)

            if CN.endswith('zip') or CN.endswith('rar') or CN.endswith('7z'):
                listfiles += f"╭─◆ **❮ /up_{count} ❯─❮ /rn_{count} ❯─❮ /dl_{count} ❯**\n"
                listfiles += f"╰📦 **{SIZE} MB - `{CN}`**\n\n"
            elif i[-3] == '0':
                listfiles += f"╭─◆ **❮ /up_{count} ❯─❮ /rn_{count} ❯─❮ /dl_{count} ❯**\n"
                listfiles += f"╰🧩 **{SIZE} MB - `{CN}`**\n\n"
            else:
                listfiles += f"╭─● **❮ /up_{count} ❯─❮ /rn_{count} ❯─❮ /dl_{count} ❯**\n"
                listfiles += f"╰➣ **{SIZE} MB - `{CN}`**\n\n"

            fileSize += SIZE

        elif isdir(f'{DIRECTORY}/{i}'):
            listfiles += f"╭─◆ **❮ /cd_{count} ❯─❮ /rn_{count} ❯─❮ /dl_{count} ❯**\n"
            listfiles += f"╰📁 `{i}`\n\n"

        DIC_ARCH[count] = i

    DIC_FILES[username] = DIC_ARCH
    listfiles += f"**⚖️ TAMAÑO TOTAL: {round(fileSize, 2)} MB\n**"
    SMS_FILES = []

    for i in LSFILES:
        SMS_DEL = SMS.reply(i)
        SMS_FILES.append(SMS_DEL)
    SMS_DEL = SMS.reply(listfiles, reply_markup=MENU,
                        disable_web_page_preview=True)
    SMS_FILES.append(SMS_DEL)

    SAVED_MESSAGES[username] = {"sms_files": SMS_FILES}
    return SAVED_MESSAGES

# ******************************************************************************************


def extractImg(File: str, username: str) -> list:
    """
    La función `extractImg` toma un archivo de video y un nombre de usuario como entrada, extrae 10
    imágenes del video a intervalos regulares y devuelve una lista de las rutas de los archivos extraídos. imágenes

    :param File: El parámetro `Archivo` es el nombre del archivo de video del que desea extraer
    imágenes. Debe ser una cadena que represente el nombre del archivo, incluida la extensión del
    archivo.

    :param username: El nombre de usuario es una cadena que representa el nombre del usuario. Se utiliza
    para crear un directorio con el nombre de usuario como nombre.

    :return: una lista de rutas de archivo de imagen.
    """
    try:
        makedirs(join(username, "IMG"))
    except:
        pass
    print("Leyendo Video")
    VIDEO = VideoCapture(join(username, File))
    TOTALFRAME = int(VIDEO.get(CAP_PROP_FRAME_COUNT))
    RESULTADO = TOTALFRAME//10

    count = 1
    ListaImg = []
    # Extrayendo 10 imágenes del video.
    for i in range(RESULTADO//2, TOTALFRAME, RESULTADO):
        VIDEO.set(CAP_PROP_POS_FRAMES, i)
        frame = VIDEO.read()[1]
        imwrite(f"./{username}/IMG/IMG-{count}.jpg", frame)
        ListaImg.append(join(username, "IMG", f"IMG-{count}.jpg"))
        count += 1

    return ListaImg


def sizeof(num: int, suffix='B'):
    """
    La función `sizeof` convierte un número dado en un formato legible por humanos con las unidades
    apropiadas (bytes, kilobytes, megabytes, etc.).

    :param num: El parámetro `num` es el número para el que desea calcular el tamaño. Representa el
    tamaño en bytes

    :param suffix: El parámetro de sufijo es opcional y el valor predeterminado es 'B'. Se utiliza para
    especificar la unidad de medida del tamaño. Por ejemplo, si el sufijo se establece en 'B', el tamaño
    se mostrará en bytes, defaults to B (optional)

    :return: La función `sizeof` devuelve una cadena formateada que representa el tamaño de un número en
    bytes, con un sufijo opcional.
    """
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def sendInfo(message):
    message.reply(message)


def cleanString(String: str):
    """
    La función `cleanString` toma una cadena como entrada y devuelve una versión limpia de la cadena
    eliminando los caracteres que no son ASCII, reemplazando los espacios con guiones bajos y eliminando
    los paréntesis.

    :param String: El parámetro "String" es una cadena que representa el texto de entrada que debe
    limpiarse

    :return: una versión limpia de la cadena de entrada.
    """
    text = normalize('NFKD', String).encode(
        'ascii', 'ignore').decode('utf-8', 'ignore')
    cleanName = ''.join(c for c in text if ord(c) < 128)
    cleanName = cleanName.replace(" ", "_").replace('(', '').replace(')', '')
    return cleanName


def extractInfoVideo(file: str, username: str):
    """
    La función `extractInfoVideo` toma un archivo de video y un nombre de usuario como entrada, extrae
    información sobre el video (como el número de fotogramas y la duración), genera una imagen en
    miniatura con una marca de agua basada en el nombre de usuario y devuelve la ruta a la imagen en
    miniatura y la duración del video en segundos.

    :param file: El parámetro `archivo` es la ruta al archivo de video del que desea extraer
    información. Debe ser una cadena que represente la ruta del archivo
    :param username: El parámetro `username` es una cadena que representa el nombre de usuario del
    usuario que solicita la extracción de la miniatura del video
    :return: el nombre de archivo de la imagen en miniatura del video generado y la duración del video
    en segundos.
    """
    VIDEO = VideoCapture(file)  # RUTA DEL VIDEO
    frames = VIDEO.get(CAP_PROP_FRAME_COUNT)
    fps = int(VIDEO.get(CAP_PROP_FPS))
    seconds = int(frames / fps)

    try:
        TOTALFRAME = int(VIDEO.get(CAP_PROP_FRAME_COUNT))
        VIDEO.set(CAP_PROP_POS_FRAMES, TOTALFRAME//randint(5, 15))
        IMG = VIDEO.read()[1]
        Alto, Ancho = IMG.shape[:2]
        if Ancho > Alto:
            Alto = int(Alto * 320 / Ancho)
            Ancho = 320
        else:
            Ancho = int(Ancho * 320 / Alto)
            Alto = 320

        IMG = resize(IMG, (Ancho, Alto))
        overlay = IMG.copy()
        alpha = 0.5
        if username == 'eduadani' or username == 'ErickYasser' or username == 'HalconVip':
            text = '@CineMaxFree'
        else:
            text = '@File_MasterBot'
        putText(img=overlay, text=text,
                org=(7, Alto-20), fontFace=FONT_HERSHEY_SIMPLEX, fontScale=0.7,
                color=(255, 255, 255), thickness=2)
        output = addWeighted(
            overlay, alpha, IMG[Alto - Alto:Alto, Ancho - Ancho:Ancho], 1 - alpha, 0)

        imwrite(splitext(basename(file))[0] + '.jpg', output)
        return splitext(basename(file))[0] + '.jpg', seconds
    except Exception as x:
        print(x)
        return "./assets/thumb.jpg", seconds


def mostrar_opciones(SMS, USER_COLLECTION, username):
    OPTION = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌠 ADD IMAGE", callback_data='tumb'), InlineKeyboardButton(
            "📤 AUTO UP.", callback_data='autoup'), InlineKeyboardButton("💬 ADD CAPTION", callback_data='caption')],
        [InlineKeyboardButton("📚 FILE FORMAT", callback_data='formatfile'), InlineKeyboardButton(
            '🗜 ZIP SIZE', callback_data='zipsize')],
        [InlineKeyboardButton("🎞 VIDEO UPLOAD", callback_data='formatvideo'), InlineKeyboardButton(
            "🏷 SAVE DESC", callback_data='savedesc')],
        [InlineKeyboardButton('⏮ REGRESAR ⏮', callback_data='backk')]])

    ZZ = USER_COLLECTION.find_one({"username": username})["zip_size"]
    YF = USER_COLLECTION.find_one({"username": username})["youtube_format"]
    FF = USER_COLLECTION.find_one({"username": username})[
        "compression_format"]
    TF = USER_COLLECTION.find_one({"username": username})["twitch_format"]
    AU = USER_COLLECTION.find_one({"username": username})["autoUpload"]
    FV = USER_COLLECTION.find_one({"username": username})["video_format"]
    SV = USER_COLLECTION.find_one({"username": username})["savedesc"]
    text = "**             ⚙️ OPTIONS ⚙️\n"
    text += "\n🌠 ADD IMAGE: __Para asignar una imagen que se mostrará en el archivo al subirlo a Telegram, envíe la imagen deseada mediante el botón correspondiente.__\n"
    text += "\n💬 ADD CAPTION: __Para añadir un caption o subtítulo personalizado a los archivos subidos por el Bot.__\n"
    text += f"\n🗜 ZIP SIZE: __Para subir los archivos a Telegram, indique el tamaño en megabytes (MB).__ [ `{ZZ} MB` ]\n"
    text += f"\n📚 FILE FORMAT: __Para comprimir los archivos y reducir su tamaño, elija el formato de compresión que prefiera entre las opciones disponibles: ZIP, 7z__ [ `{FF}` ]\n"
    text += f"\n📤 AUTO UP.: __Para activar o desactivar la subida automática de los archivos descargados a Telegram, marque o desmarque la casilla correspondiente.__ [ `{AU}` ]\n"
    text += f"\n🎞 VIDEO UPLOAD: __Para elegir si los vídeos se subirán a Telegram como documento o como vídeo, seleccione la opción que prefiera entre las dos disponibles.__ [ `{FV}` ]\n"
    text += f"\n🏷 SAVE DESC: __Para guardar los archivos con el nombre que aparece en su descripción.__ [ `{SV}` ]\n**"
    SMS.reply(text, reply_markup=OPTION)

def download_youtube(message, URL, CHOSE_FORMAT, username, SAVED_MESSAGES): 
    sms = message.reply_sticker('./assets/loading.tgs')
    count = 0
    FormatList = {}
    Botones = []
    for f in YoutubeDL().info(URL):
        count += 1
        FormatList[count] = f.split(":")
        if "youtu" in URL:
            if f.split(":")[0].isdigit():
                if int(f.split(":")[0]) > 100 and 'audio' not in f.split(":")[1]:
                    Botones.append([InlineKeyboardButton(
                        f'🔇 {f.split(":")[1]} [{f.split(":")[2]}] ~ {f.split(":")[3]}', callback_data=f"dlvid-{count}")])
                else:
                    Botones.append([InlineKeyboardButton(
                        f'{f.split(":")[1]} [{f.split(":")[2]}] ~ {f.split(":")[3]}', callback_data=f"dlvid-{count}")])
        else:
            Botones.append([InlineKeyboardButton(
                f'{f.split(":")[1]} [{f.split(":")[2]}] ~ {f.split(":")[3]}', callback_data=f"dlvid-{count}")])
    CHOSE_FORMAT[username] = FormatList
    BTN_FORMATS = InlineKeyboardMarkup(Botones)
    caption = f"\n**{YoutubeDL().metaInfo(URL)['Title']}**"
    r = get(YoutubeDL().metaInfo(URL)['Thumb'])
    with open(f'{username}.jpg', 'wb') as img:
        img.write(r.content)
    sms_video = message.reply_photo(
        f'{username}.jpg', caption=caption, reply_markup=BTN_FORMATS, quote=True)
    sms.delete()
    unlink(f'{username}.jpg')
    SAVED_MESSAGES[username] = {"sms_video": sms_video}
    return CHOSE_FORMAT, SAVED_MESSAGES