import requests
import os
import gdown
import instaloader
from ModulesDownloads.mega_bar import download_url_with_progress
from ModulesDownloads.wallhavendl import wallhavendl
from ModulesDownloads.wget import download as downloadwget
from ModulesDownloads.mediafire import get
from pyrogram.errors import ChannelInvalid
from UploadFiles import *
from user_agent import generate_user_agent
from progrs import progressddl, progresstwitch, progressytdl, progresswget
from ModulesDownloads.youtubedl import YoutubeDL as customYoutubeDL
from tools import download_of_youtube
from drive_dl import gdl, complete_gdl
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from gdown import download
from random import choice
from time import time
from download_playlist import descargar_playlist

try:
    from mega import Mega
except:
    pass
from yt_dlp import YoutubeDL

NAME_APP = os.getenv("NAME_APP")

# CREDENCIALES DE GOOGLE DRIVE
gauth = GoogleAuth(settings_file="./conf.yaml")
gauth.LoadCredentialsFile("credentials_module.json")

if gauth.access_token_expired:
    gauth.Refresh()
    gauth.SaveCredentialsFile("credentials_module.json")
else:
    gauth.Authorize()

drive = GoogleDrive(gauth)
dlinsta = instaloader.Instaloader(
    download_comments=False,
    download_geotags=False,
    download_pictures=False,
    download_video_thumbnails=False,
    save_metadata=False,
    compress_json=False,
)

dlinsta.load_session_from_file(
    username="devmaster_one", filename="./session-devmaster_one"
)


def DownloadFiles(
    app, userbot, message_id, url, username, directory, format, left, options
):
    keywords = [
        "youtu.be",
        "twitch",
        "fb.watch",
        "www.xvideos.com",
        "www.xnxx.com",
        "www.yourupload.com",
    ]

    if any(keyword in url for keyword in keywords):
        sms = app.send_message(message_id, "📥 **Downloading Video**")
        try:
            if "youtu" in url:
                if int(format[0]) > 100:
                    ydl_opts = {"skip_download": True}
                    with YoutubeDL(ydl_opts) as ydl:
                        info_dict = ydl.extract_info(url, download=False)
                        video_title = info_dict.get("title", None)
                    format = format[0].split(sep=("("))[-1].replace(")", "")
                    file = "./" + directory + "/" + video_title + ".%(ext)s"
                    ydl_opts = {
                        "format": format,
                        "outtmpl": file,
                        "restrict_filenames": True,
                        "windowsfilenames": False,
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    FILE = file
                else:
                    FILE = download_of_youtube(sms, format, app, url, directory)[
                        0
                    ].split("/")[-1]
            else:
                FILE = download_of_youtube(sms, format, app, url, directory)[0].split(
                    "/"
                )[-1]

            if options["auto_up"] == "up_noCompress":
                uploadOnefile(app, sms, FILE, directory, left, options)
            else:
                sms.edit_text("✅ **Download complete**")
        except Exception as x:
            sms.edit_text(x)
        return

    elif "mediafire" in url:
        sms = app.send_message(message_id, "📥 **Downloading from Mediafire**")
        try:
            FILE = downloadwget(
                get(url), sms, app, out=f"{directory}", bar=progresswget
            )
            FILE = FILE.split("/")[-1]
            sms.edit_text("✅ **Download complete**")

        except Exception as x:
            sms.edit_text(f"❌ **No se pudo descargar el archivo: \n{x}** ❌")
        return

    elif "www.instagram.com" in url:
        sms = app.send_message(message_id, "📥 **Downloading from Instagram**")
        post = instaloader.Post.from_shortcode(dlinsta.context, url.split("/")[-2])
        dlinsta.download_post(post, target=directory)
        sms.edit_text("✅ **Download complete**")

    elif "wallhaven.cc" in url:
        try:
            num = url.split(" ")[-1]
            if not num.isdigit():
                num = 0
            sms = app.reply_sticker(message_id, "./assets/loading.tgs")
            wallpaper = wallhavendl(url.split(" ")[0], int(num))
            emojis = (
                "🗾",
                "🎑",
                "🏞",
                "🌅",
                "🌄",
                "🌠",
                "🎇",
                "🎆",
                "🌇",
                "🌆",
                "🏙",
                "🌃",
                "🌌",
                "🌉",
                "🌁",
            )
            sms.delete()
            sms = app.send_message(message_id, "🏙 **Imágenes descargadas: **")
            for count, link in enumerate(wallpaper):
                with open(join(directory, link.split("/")[-1]), "wb") as d:
                    d.write(requests.get(link).content)
                sms.edit_text(f"{choice(emojis)} **Imágenes descargadas: {count+1}**")
            sms.edit_text("✅ **Download complete**")

        except Exception as x:
            app.send_message(message_id, x)
        return

    elif "drive.google.com/drive/folders" in url:
        sms = app.send_message(message_id, "📥 **Downloading folder from Google Drive**")
        try:
            try:
                filename = gdown.download_folder(
                    url, use_cookies=False, output=directory + "/"
                )
            except:
                sms = complete_gdl(drive, url, sms, directory)

        except Exception as x:
            sms.edit_text(f"❌ **No se pudo descargar el archivo:\n{x}** ❌")
        return

    elif "mega.nz" in url:
        sms = app.send_message(message_id, "📥 **Downloading from Mega**")
        try:
            Mega.download_url_with_progress = download_url_with_progress
            m = Mega()
            m.login()
            m.download_url(url=url, dest_path=directory)
            # m.download_url_with_progress(url, directory)
            sms.edit_text("✅ **Download complete**")
        except Exception as x:
            sms.edit_text(f"❌ **Download Failed**")
        return

    elif "drive.google.com" in url:
        sms = app.send_message(message_id, "📥 **Downloading file from Google Drive**")
        try:
            FILE = download(url=url, output=directory + "/")
            # FILE = gdl(drive, url, sms)

            sms.edit_text("✅ **Download complete**")
        except Exception as x:
            sms.edit_text(f"❌ **No se pudo descargar el archivo: \n\n{x}** ❌")
        return

    elif "youtube.com/playlist" in url:
        sms = app.send_message(message_id, "📥 **Downloading Playlist**")
        try:
            descargar_playlist(url=url, path=directory)
            # ytdl = customYoutubeDL(progresstwitch, sms, app, isTwitch=True)
            # title = ytdl.downloadlist(url, directory)
            # NM_ZIP = title[1]
            # FOLDER_FILES = listdir(title[0])
            sms.edit_text("✅ **Download complete**")
        except Exception as x:
            sms.edit_text(f"❌ **No se pudo descargar la Playlist: \n{x}** ❌")
        return

    elif url.startswith("http") and "t.me/" not in url:
        sms = app.send_message(message_id, "📥 **Downloading File...**")
        try:
            filename = downloadwget(url, sms, app, out=f"{directory}", bar=progresswget)
            FILE = filename.split("/")[-1]
            sms.edit_text("✅ **Download complete**")
        except:
            try:
                r = requests.get(url, headers={"user-agent": generate_user_agent()})
                with open(f"{directory}/{url.split('/')[-1]}", "wb") as f:
                    f.write(r.content)
                FILE = url.split("/")[-1]
                sms.edit_text("✅ **Download complete**")
            except Exception as x:
                sms.edit_text(f"❌ **No se pudo descargar el archivo: \n{x}** ❌")

    # Descargar de Canales Restringidos
    if url.startswith("https://t.me/"):
        sms = app.send_message(message_id, "📥 **Downloading File...**")
        if url.endswith("?single"):
            url = url.replace("?single", "")
        # try:
        if url.startswith("https://t.me/c/"):
            try:
                chat = "-100" + url.split("/")[-2]
                msg_id = url.split("/")[-1]
                msge = userbot.get_messages(int(chat), int(msg_id))
                if msge.media:
                    msg = app.send_message(message_id, "**📥 Descargando...**")
                    start = time()
                    file = userbot.download_media(
                        msge,
                        file_name=f"{username}/",
                        progress=progressddl,
                        progress_args=(sms, start, 0),
                    )
                    msg.edit_text(f"✅ **`{file.split('/')[-1]}` DESCARGA FINALIZADA**")
            except ChannelInvalid:
                try:
                    msg.delete()
                except:
                    pass
                app.send_message(
                    message_id,
                    "**⚠️ PRIMERO DEBE INTRODUCIR EL ENLACE DE INVITACIÓN DEL CANAL**",
                )
        else:
            try:
                chat = url.split("/")[-2]
                msg_id = url.split("/")[-1]
                msge = userbot.get_messages(chat, int(msg_id))
                if msge.media:
                    msg = app.send_message(message_id, "**📥 Descargando...**")
                    start = time()
                    file = userbot.download_media(
                        msge,
                        file_name=f"{username}/",
                        progress=progressddl,
                        progress_args=(sms, start, 0),
                    )
                    msg.edit_text(f"✅ **`{file.split('/')[-1]}` DESCARGA FINALIZADA**")
            except ChannelInvalid:
                try:
                    msg.delete()
                except:
                    pass
                app.send_message(
                    message_id,
                    "**⚠️ PRIMERO DEBE INTRODUCIR EL ENLACE DE INVITACIÓN DEL CANAL**",
                )
        # except Exception as x:
        #     print(x)
        #     app.send_message(message_id, '**🚫 ENLACE INCORRECTO**')
