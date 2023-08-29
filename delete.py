from pydrive2.drive import GoogleDrive
from pyrogram.types import Message, CallbackQuery



def delete(msg: Message, drive: GoogleDrive, file_id):
    
    try:
        # message = await msg.reply(f"Eliminando {CROSS_MARK}{file1['title']}{CROSS_MARK}...")
        file1 = drive.CreateFile({'id': file_id})
        file1.Upload()
        file1.Delete()
        msg.reply(f"Se ha borrado correctamente {file1['title']}😋")
    except Exception as e:
        print(e)
        msg.reply(f"❌Error al borrar")