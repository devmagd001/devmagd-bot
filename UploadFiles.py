import zipfile
import pyminizip
import py7zr
import cv2
import time
from pyrogram import enums
from pyrogram.enums import MessageEntityType
from pyrogram.types import MessageEntity            
from progrs import progressupl
from ModulesDownloads.compress import split, getBytes
from os import getenv, mkdir, makedirs, unlink, listdir
from os.path import isfile, join, getsize, exists
from pickle import loads
from random import randint
from ModulesDownloads.file_tipeClass import fileType
from tools import cleanString, extractInfoVideo

NAME_APP = getenv("NAME_APP")

# ****************************************************************************************************************** #
# ******************************************* SUBIR ARCHIVOS COMPRIMIDOS ******************************************* #
# ****************************************************************************************************************** #

async def uploadFiles(app, message, NM_ZIP, DIRECTORY, FOLDER_FILES, USER_COLLECTION):
    CHAT_ID = message.chat.id
    USERNAME = message.from_user.username
    try: makedirs(f"folderZip/{USERNAME}")
    except: pass
    try: mkdir(f'./storage')
    except:pass
    
    if len(NM_ZIP.split('\n')) == 1: NAME = NM_ZIP
    else: NAME, PASSWORD = NM_ZIP.split('\n')
    sms = await message.reply("**📚 Comprimiendo: **")
    NAME_ZIP = f'{NAME}.zip'
    NAME_ZIP = NAME_ZIP.replace(' ', '-')
    # FOLDER_ZIP = join(DIRECTORY, NAME_ZIP)
        
    if NAME_ZIP.endswith('7z'): # ==================================================== COMPRIMIR A 7z
        if len(NM_ZIP.split('\n')) == 1: filesZip = py7zr.SevenZipFile(NAME_ZIP, 'w')
        elif len(NM_ZIP.split('\n')) == 2: filesZip = py7zr.SevenZipFile(NAME_ZIP, 'w', password=PASSWORD)
        for file in FOLDER_FILES:
            if isfile(join(DIRECTORY, file)):
                await sms.edit_text(f'**📚 Comprimiendo: `{file}`**') 
                filesZip.write(join(DIRECTORY, file))
        filesZip.close()
            
    if NAME_ZIP.endswith('zip'): # ==================================================== COMRIMIR A ZIP
        if len(NM_ZIP.split('\n')) == 1: 
            filesZip = zipfile.ZipFile(NAME_ZIP, "w")
            for file in FOLDER_FILES:
                if isfile(join(DIRECTORY, file)):
                    await sms.edit_text(f'**📚 Comprimiendo: `{file}`**')
                    filesZip.write(join(DIRECTORY, file), compress_type=zipfile.ZIP_DEFLATED)
            filesZip.close()
        else:
            files = []
            rutas = []
            for file in FOLDER_FILES:
                if isfile(join(DIRECTORY, file)):
                    files.append(join(DIRECTORY, file))
                    rutas.append(DIRECTORY)
            pyminizip.compress_multiple(files, rutas, NAME_ZIP, PASSWORD, 9)
            # NAME_ZIP = join(DIRECTORY, NAME_ZIP)
        
    if round(getsize(NAME_ZIP) / 1000000, 2) > USER_COLLECTION.find_one({'username':USERNAME})['zip_size']: # SI EL ARCHIVO PESA MAS DE 2GB
        await sms.edit_text(f"✂️ **Dividiendo en partes de: {USER_COLLECTION.find_one({'username':USERNAME})['zip_size']} MB**")
        split(f'./{NAME_ZIP}', f'./folderZip/{USERNAME}', getBytes(f"{USER_COLLECTION.find_one({'username':USERNAME})['zip_size']}.0MiB"))
        fileOrd = listdir(f'folderZip/{USERNAME}')
        fileOrd.sort()
        count = 0
        sms.delete()
        pin = await message.reply(f'⚜️◤━━━ ☆. **{NAME}** .☆ ━━━◥⚜️')
        for f in fileOrd:
            if exists(f"./{USERNAME}-thumb.jpg"): thumb = f"./{USERNAME}-thumb.jpg"
            else: thumb = "./assets/thumb.jpg"
            count += 1
            sms = await message.reply(f"**📤 Subiendo: {count}-{len(fileOrd)}**")
            await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
            start = time.time()
            try: await app.send_document(CHAT_ID, join(f"folderZip/{USERNAME}", f), thumb=thumb, progress=progressupl, progress_args=(sms, len(fileOrd), count, start))
            except: 
                return await sms.edit_text('⚠️ **UPLOADING ERROR**')
            unlink(join(f"folderZip/{USERNAME}", f))
            await sms.delete()
        await app.send_sticker(CHAT_ID, "./assets/fin.webp")   
    else:
        if exists(f"./{USERNAME}-thumb.jpg"): thumb = f"./{USERNAME}-thumb.jpg"
        else: thumb = "./assets/thumb.jpg"
        await sms.edit_text(f"**📤 Subiendo...**")
        try: SIZE = round(getsize(NAME_ZIP) / 1000024, 2)
        except: SIZE = "➖"
        
        try: DESCAP = loads(USER_COLLECTION.find_one({'username':USERNAME})['caption'])
        except: DESCAP = 'None'
        if DESCAP == 'None': 
            caption = f"**● Nombre:** __{NAME_ZIP.split('/')[-1]}__\n**● Tamaño:** __{SIZE} MB__\n\n**👑 Uploaded by:** __@File_MasterBot__"
            ENT = []
        else:
            if DESCAP['entities'] == None: ENT = []
            else: ENT = DESCAP['entities']
            
            
            MSG = DESCAP['text']
            if '{name}' in MSG and '{size}' not in MSG: 
                caption = MSG.format(name = NAME_ZIP.split('/')[-1])
            elif '{size}' in MSG and '{name}' not in MSG: 
                caption = MSG.format(size = SIZE)
            elif '{name}' in MSG and '{size}' in MSG: 
                caption = MSG.format(size = SIZE, name = NAME_ZIP.split('/')[-1])
            else: caption = MSG

        await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
        start = time.time() 
        try: pin=await app.send_document(CHAT_ID, NAME_ZIP, thumb=thumb, progress=progressupl, progress_args=(sms, 1, 1, start), caption = caption, caption_entities=ENT)
        except: 
            return await sms.edit_text('⚠️ **UPLOADING ERROR**')
            
        unlink(NAME_ZIP)
        await sms.delete()
    try: 
        if len(NM_ZIP.split('\n')) == 2: await message.reply(f"**Contraseña: **[ `{PASSWORD}` ]")
    except: pass
    delpin = await pin.pin(both_sides=True)
    await delpin.delete()
 
# ******************************************************************************************************** #
# ******************************************* SUBIR UN ARCHIVO ******************************************* #
# ******************************************************************************************************** #

async def uploadOnefile(app, message, FILE_NAME, DIRECTORY, USER_COLLECTION, TOTAL, count):
    USERNAME = message.from_user.username
    CHAT_ID = message.chat.id
    try: makedirs(f"folderZip/{USERNAME}")
    except: pass
    await message.delete()
    FILE_NAME = join(DIRECTORY, FILE_NAME)

    if round(getsize(FILE_NAME) / 1000000, 2) > USER_COLLECTION.find_one({'username':USERNAME})['zip_size']: # SI EL ARCHIVO PESA MAS DE 2GB
        await message.reply(f"✂️ **Dividiendo en partes de: {USER_COLLECTION.find_one({'username':USERNAME})['zip_size']} MB**")
        split(f'./{FILE_NAME}', f'./folderZip/{USERNAME}', getBytes(f"{USER_COLLECTION.find_one({'username':USERNAME})['zip_size']}.0MiB"))
        fileOrd = listdir(f'folderZip/{USERNAME}')
        fileOrd.sort()
        num = 0
        await message.delete()
        pin = await message.reply(f"⚜️◤━━━ ☆. **{FILE_NAME.split('/')[-1]}** .☆ ━━━◥⚜️")
        for f in fileOrd:
            if exists(f"./{USERNAME}-thumb.jpg"): thumb = f"./{USERNAME}-thumb.jpg"
            else: thumb = "./assets/thumb.jpg"
            num += 1
            sms = await message.reply(f"**📤 Subiendo: {num}-{len(fileOrd)}**")
            await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
            start = time.time()
            await app.send_document(CHAT_ID, join(f"folderZip/{USERNAME}", f), thumb=thumb, progress=progressupl, progress_args=(sms, len(fileOrd), num, start))
            unlink(join(f"folderZip/{USERNAME}", f))
            await sms.delete()
        await app.send_sticker(CHAT_ID, "./assets/fin.webp")
        delpin = await pin.pin(both_sides=True)
        await delpin.delete()
    else:
        if exists(f"./{USERNAME}-thumb.jpg"): thumb = f"./{USERNAME}-thumb.jpg"
        else: thumb = "./assets/thumb.jpg"
        sms = await message.reply(f"**📤 Subiendo: {count}-{TOTAL}**")
        try: SIZE = round(getsize(FILE_NAME) / 1000024, 2)
        except: SIZE = "➖"
        NAME = FILE_NAME.split('/')[-1]
        ENT = []
        try: DESCAP = loads(USER_COLLECTION.find_one({'username':USERNAME})['caption'])
        except: DESCAP = 'None'
        if DESCAP == 'None': 
            caption = f"**● Nombre:** __{NAME}__\n**● Tamaño:** __{SIZE} MB__\n\n**👑 Uploaded by:** __@File_MasterBot__"
        else:
            caption = f"● Nombre: {NAME}\n● Tamaño: {SIZE} MB\n\n"
            LEN = len(caption)
            caption += DESCAP['text']
            ENT.append(MessageEntity(type = MessageEntityType.BOLD, offset = caption.index('● Tamaño:'), length = len('● Tamaño:')))  
            ENT.append(MessageEntity(type = MessageEntityType.BOLD, offset = caption.index('● Nombre:'), length = len('● Nombre:'))) 
            ENT.append(MessageEntity(type = MessageEntityType.ITALIC, offset = caption.index(NAME), length = len(NAME)))
            ENT.append(MessageEntity(type = MessageEntityType.ITALIC, offset = caption.index(f'{SIZE} MB'), length = len(f'{SIZE} MB')))
            for i in DESCAP['entities']: ENT.append(MessageEntity(type = i.type, offset = i.offset + LEN, length = i.length))
        
            if USERNAME != 'eduadani' and USERNAME != 'ErickYasser' and USERNAME != 'HalconVip':
                caption += '\n\n👑 Uploaded by: @File_MasterBot'
                ENT.append(MessageEntity(type = MessageEntityType.BOLD, offset = caption.index('👑 Uploaded by:'), length = len('👑 Uploaded by:')))
                ENT.append(MessageEntity(type = MessageEntityType.ITALIC, offset = caption.index('@File_MasterBot'), length = len('@File_MasterBot')))
            
        start = time.time()
        if fileType(file=FILE_NAME).isVideo():
            if USER_COLLECTION.find_one({'username': USERNAME})["video_format"] == 'Video':
                THUMB, seconds = extractInfoVideo(FILE_NAME, USERNAME)
                await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_VIDEO) 
                await app.send_video(CHAT_ID , FILE_NAME, progress=progressupl, progress_args=(sms, TOTAL, count, start), duration=seconds, thumb=THUMB, caption=caption, caption_entities=ENT)
            else:
                await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
                await app.send_document(CHAT_ID, FILE_NAME, progress=progressupl, progress_args=(sms, TOTAL, count, start), thumb=thumb, caption=caption, caption_entities=ENT)
            await sms.delete()
        else:
            if fileType(file=FILE_NAME).isPhoto():
                try:
                    await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_PHOTO)
                    await app.send_photo(CHAT_ID, FILE_NAME)
                except:
                    await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
                    await app.send_document(CHAT_ID, FILE_NAME, thumb=thumb, progress=progressupl, progress_args=(sms, TOTAL, count, start), caption=caption, caption_entities=ENT)
            else:
                await app.send_chat_action(CHAT_ID, enums.ChatAction.UPLOAD_DOCUMENT)
                await app.send_document(CHAT_ID, FILE_NAME, thumb=thumb, progress=progressupl, progress_args=(sms, TOTAL, count, start), caption=caption, caption_entities=ENT)
            await sms.delete()
              
# ********************************************************************************************************** #
# ******************************************* COMPRIMIR ARCHIVOS ******************************************* #
# ********************************************************************************************************** #
        
def compressfiles(app, message, msg, DIRECTORY, USER_COLLECTION):
    
    password = ""
    if len(msg.split('\n')) == 1: name = msg
    else: name, password = msg.split('\n')
    folderFiles = listdir(DIRECTORY)
    sms = message.reply("**📚 Comprimiendo: **")
    nameZip = f'{name}.zip'
    nameZip = nameZip.replace(' ', '-')
    
    if nameZip.endswith('7z'): # ==================================================== COMPRIMIR A 7z
        if len(msg.split('\n')) == 1: filesZip = py7zr.SevenZipFile(nameZip, 'w')
        elif len(msg.split('\n')) == 2: filesZip = py7zr.SevenZipFile(nameZip, 'w', password=password)
        for file in folderFiles:
            if isfile(join(DIRECTORY, file)):
                sms.edit_text(f'**📚 Comprimiendo: `{file}`**') 
                filesZip.write(join(DIRECTORY, file))
        filesZip.close()
            
    if nameZip.endswith('zip'): # ==================================================== COMRIMIR A ZIP
        files = []
        rutas = []
        if password == "":
            zf = zipfile.ZipFile(join(DIRECTORY, nameZip), 'w')
            for file in folderFiles:
                if isfile(join(DIRECTORY, file)):
                    sms.edit_text(f'**📚 Comprimiendo: `{file}`**') 
                    zf.write(join(DIRECTORY, file))
            zf.close()
        else:
            for file in folderFiles:
                if isfile(join(DIRECTORY, file)):
                    files.append(join(DIRECTORY, file))
                    rutas.append(DIRECTORY)
            pyminizip.compress_multiple(files, rutas, join(DIRECTORY, nameZip), password, 9)
            message.reply(f"**Contraseña: `{password}`**")
        sms.delete()

# ************************************************************************************************************************ #
# ******************************************* COMPRIMIR ARCHIVOS SELECCIONADOS ******************************************* #
# ************************************************************************************************************************ #

def compressSelectedFiles(message, NAME, USERNAME, listCompress, USER_COLLECTION, DIRECTORY):
    password = ""
    if len(NAME.split('\n')) == 1: name = NAME
    else: name, password = NAME.split('\n')
    sms = message.reply("**📚 Comprimiendo: **")
    nameZip = f'{USERNAME}/{name}.{USER_COLLECTION.find_one({"username":USERNAME})["compression_format"]}'
    nameZip = nameZip.replace(' ', '-')
         
    if nameZip.endswith('7z'): # ==================================================== COMPRIMIR A 7z
        if len(NAME.split('\n')) == 1: filesZip = py7zr.SevenZipFile(nameZip, 'w')
        elif len(NAME.split('\n')) == 2: filesZip = py7zr.SevenZipFile(nameZip, 'w', password=password)
        for file in listCompress:
            if isfile(join(DIRECTORY, file)):
                sms.edit_text(f'**📚 Comprimiendo: `{file}`**') 
                filesZip.write(join(DIRECTORY, file))
        filesZip.close()
            
    if nameZip.endswith('zip'): # ==================================================== COMRIMIR A ZIP
        files = []
        rutas = []
        if password == "":
            zf = zipfile.ZipFile(nameZip, 'w')
            for file in listCompress:
                if isfile(join(DIRECTORY, file)):
                    sms.edit_text(f'**📚 Comprimiendo: `{file}`**') 
                    zf.write(join(DIRECTORY, file))
            zf.close()
        else:
            for file in listCompress:
                if isfile(join(DIRECTORY, file)):
                    files.append(join(DIRECTORY, file))
                    rutas.append(DIRECTORY)
            pyminizip.compress_multiple(files, rutas, nameZip, password, 9)
            message.reply(f"**Contraseña: `{password}`**")
        sms.delete()