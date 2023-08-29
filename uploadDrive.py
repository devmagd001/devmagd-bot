from pydrive2.drive import GoogleDrive
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton as IKB, CallbackQuery 

def upload_to_tdd(drive: GoogleDrive, filename: str, msg: Message = None, length = None):
    
    INDEX_LINK = "https://tg-bot.leecherboy.workers.dev/0:/Grupo%20Escuela/"
    
    metadata = {
    'title': filename,
    'parents': [{
        'teamDriveId': '0AN5Lkp8pZu3HUk9PVA',
        'id': '1iGFy-8kT4wJH0IrZi-T4UVPWnsF15UmY'
    }]
    }

    tdd_file = drive.CreateFile(metadata)

    message = msg.reply("Subiendo {}".format(tdd_file['title']))

    tdd_file.SetContentFile(tdd_file['title'])
    tdd_file['title'] = filename.split('/')[-1]
    tdd_file.Upload()

    message.delete()

    msg.reply("**✅ Tarea finalizada \n\n📄 Nombre: `{}` \n📚 Tamaño: `{}` \n🆔 del Archivo: `{}`**".format(filename.split("/")[-1], length, tdd_file['id']), 
    reply_markup=InlineKeyboardMarkup(
        [
            [
                IKB("Index Link", url=str(INDEX_LINK+filename.split("/")[-1].replace(" ", "%20")+"?a=view"))
            ]
        ]
        ))

    return tdd_file