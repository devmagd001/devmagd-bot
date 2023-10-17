import yt_dlp
from pyrogram import Client, dispatcher, filters
import tgcrypto
import asyncio
import unicodedata
import random
import re


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    ext = str(value).split(".")[-1]
    value = str(value).split(".")[0]
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def my_hook(d):
    if d["status"] == "downloading":
        filemane = d["filename"]
        current = d["downloaded_bytes"]
        total = d["total_bytes"]
        speed = d["speed"]
        print(f"Descargando {current * 100 / total:.1f} --- {speed}")
    if d["status"] == "finished":
        print("Done downloading, now converting ...")


def info(url):
    ydl_opts = {"restrict_filenames": True, "windowsfilenames": False}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(url, download=False)

    formats = meta["formats"]
    id = []
    ext = []
    formato = []
    for format in formats:
        if format["vcodec"] != "none" and format["acodec"] != "none":
            # if 'DASH' in str(format['format']):
            #     continue
            # if 'mp4' == str(format['ext']):
            id.append(format["format_id"])
            ext.append(format["ext"])
            formato.append(format["format"].split(sep="-")[-1])
    guardar = []
    for val1, val2, val3 in zip(id, ext, formato):
        guardar.append(val1 + ":" + val3 + ":" + val2)
    return guardar


def getTitle(url):
    elem = "abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ids = "".join(random.sample(elem, 4))
    ydl_opts = {"restrict_filenames": True, "windowsfilenames": False}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(url, download=False)
        title = meta["title"] + ids
        return slugify(title)


def getPlaylist(url):
    elem = "abcdefgh1jklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ids = "".join(random.sample(elem, 4))
    ydl_opts = {"restrict_filenames": True, "windowsfilenames": False}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(url, download=False)
        playlist = str(meta["title"]) + ids
        return slugify(playlist)


def download(url, username, res):
    title = getTitle(url)
    file = "./" + username + "/" + title + ".%(ext)s"
    format = format.split(sep=("("))[-1].replace(")", "")
    opcions = {
        "format": f"b[height<={res}]",
        "outtmpl": file,
        "restrict_filenames": True,
        "windowsfilenames": False,
    }

    with yt_dlp.YoutubeDL(opcions) as ydl:
        ydl.download([url])
        meta = ydl.extract_info(url, download=False)
        name = "./" + username + "/" + title + ".mp4"
        duration = int(meta["duration"])
    return name, duration


def downloadlist(urls, username, format):
    playlist = getPlaylist(urls)
    file = "./" + username + "/%(title)s.%(ext)s"
    ydl_opts = {
        # 'format': f'b[height<={res}]',
        "format": format,
        "outtmpl": file,
        "restrict_filenames": False,
        "windowsfilenames": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([urls])
        dir = "./" + username + "/" + playlist + "/"
        name = playlist
        return dir, name
