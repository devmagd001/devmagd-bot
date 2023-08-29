from pydrive2.drive import GoogleDrive
from pyrogram.types import Message
from os import mkdir, listdir
from os.path import exists

def gdl(drive: GoogleDrive, url: str, message: Message):
    metadata = {
        'id': url.split("/")[-2]
    }

    Gfile = drive.CreateFile(metadata=metadata)
    Gfile.GetContentFile(Gfile['title'])
    return Gfile['title']

def folder_gdl(drive: GoogleDrive, url: str, message: Message, directory:str):
    # EJEMPLO DE ENLACES:
    # https://drive.google.com/drive/u/1/folders/0AN5Lkp8pZu3HUk9PVA
    # O SEA, DEBE ESTAR EL ID AL FINAL DEL ENLACE
    
    if url.endswith('?usp=share_link'):
        url = url.replace('?usp=share_link', '')
    
    message.edit("**Descargando:**")
    folder_url = url.split("/")[-1]
    folder = drive.CreateFile({'id': folder_url})
    folder.FetchMetadata()
    metadata = {
        'q': f"'{folder_url}' in parents and trashed=false"
    }
    nameFolder = folder['title'].replace(" ", "_")
    try: mkdir(f"./{directory}/{nameFolder}/")
    except:pass

    GFolder = drive.ListFile(metadata).GetList()
    for file1 in GFolder:
        message.edit(f"**Descargando: **`{file1['title']}`")
        file1.GetContentFile(f"./{directory}/{nameFolder}/" + file1['title'])
    
    return message 

def complete_gdl(drive: GoogleDrive, url: str, message: Message, DIRECTORY: str):
    if url.endswith('?usp=share_link'):
        url = url.replace('?usp=share_link', '')
        
    folder_id = url.split("/")[-1]
    metadata = {
        'q': f"'{folder_id}' in parents and trashed=false"
    }

    father_folder = drive.ListFile(metadata).GetList()
    try:
        for folder in father_folder:

            child_folder = drive.ListFile({'q':f"'{folder['id']}' in parents and trashed=false"}).GetList()
            if folder['mimeType'] == 'application/vnd.google-apps.folder':
                FOLDER_NAME = folder['title'].replace(" ", "_")
                if not exists(f"./{DIRECTORY}/" + FOLDER_NAME):
                    mkdir(f"./{DIRECTORY}/" + FOLDER_NAME)

                for files in child_folder:
                    # print(files['id'])
                    print('Descargando ' + files['title'])
                    files.GetContentFile(f"./{DIRECTORY}/" + FOLDER_NAME + "/" + files['title'])
                    print('Finalizado')
    except: 
        pass
    try: 
        for under_files in father_folder:
            if under_files['mimeType'] != 'application/vnd.google-apps.folder':
                print("Descargando " + under_files['title'])
                under_files.GetContentFile("./{DIRECTORY}/" + under_files['title'])
                print('Finalizado')
    except: 
        pass
    return message
